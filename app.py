from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from flask import Flask, render_template, request
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

app = Flask(__name__)
LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://127.0.0.1:8085").rstrip("/")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "mistral")
LOCAL_LLM_TIMEOUT = float(os.getenv("LOCAL_LLM_TIMEOUT", "20"))
_LLM_BOOTED = False
_LLM_BOOT_ERROR = ""


@dataclass
class RiskAlert:
    shipment_id: str
    supplier: str
    supplier_id: str
    origin_country: str
    risk_reason: str
    severity: float


def load_json(filename: str) -> List[Dict[str, Any]]:
    with (DATA_DIR / filename).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def index_by(items: List[Dict[str, Any]], key: str) -> Dict[str, Dict[str, Any]]:
    return {item[key]: item for item in items}


def build_trade_block_scenario(news: List[Dict[str, Any]]) -> Dict[str, Any]:
    block_event = next((item for item in news if "trade block" in item["headline"].lower()), None)
    if not block_event:
        return {
            "title": "No trade block detected",
            "summary": "No active trade block events were detected in the news feed.",
            "affected_countries": [],
            "severity": 0.0,
        }
    return {
        "title": block_event["headline"],
        "summary": block_event["summary"],
        "affected_countries": block_event["affected_countries"],
        "severity": block_event["severity"],
        "timestamp": block_event["timestamp"],
        "source_url": block_event.get("source_url", ""),
    }


def generate_risk_alerts(
    shipments: List[Dict[str, Any]],
    suppliers: Dict[str, Dict[str, Any]],
    scenario: Dict[str, Any],
) -> List[RiskAlert]:
    alerts: List[RiskAlert] = []
    for shipment in shipments:
        supplier = suppliers[shipment["supplier_id"]]
        if supplier["country"] in scenario["affected_countries"]:
            alerts.append(
                RiskAlert(
                    shipment_id=shipment["shipment_id"],
                    supplier=supplier["name"],
                    supplier_id=supplier["supplier_id"],
                    origin_country=supplier["country"],
                    risk_reason="Trade block exposure for China-origin electronics.",
                    severity=scenario["severity"],
                )
            )
    return alerts


def suggest_alternatives(
    suppliers: List[Dict[str, Any]],
    target_category: str,
    blocked_countries: List[str],
) -> List[Dict[str, Any]]:
    alternatives = [
        supplier
        for supplier in suppliers
        if supplier["category"] == target_category and supplier["country"] not in blocked_countries
    ]
    alternatives.sort(key=lambda item: (item["performance_score"], -item["lead_time_days"]), reverse=True)
    return alternatives


def summarize_shipments(shipments: List[Dict[str, Any]]) -> Dict[str, Any]:
    delayed = [shipment for shipment in shipments if shipment["status"].lower().startswith("delayed")]
    return {
        "total": len(shipments),
        "delayed": len(delayed),
        "delay_rate": round(len(delayed) / len(shipments), 2) if shipments else 0,
    }


def answer_question(question: str, suppliers: Dict[str, Dict[str, Any]], performance: Dict[str, Dict[str, Any]]) -> str:
    normalized = question.lower()
    if "supplier" in normalized and ("performance" in normalized or "score" in normalized):
        ranked = sorted(
            performance.values(), key=lambda item: item["last_quarter_score"], reverse=True
        )
        top_supplier = suppliers[ranked[0]["supplier_id"]]["name"]
        return (
            f"Top supplier performance this quarter is {top_supplier} "
            f"with score {ranked[0]['last_quarter_score']} and on-time rate {ranked[0]['on_time_rate']:.0%}."
        )
    if "delay" in normalized or "late" in normalized:
        worst = min(performance.values(), key=lambda item: item["on_time_rate"])
        supplier_name = suppliers[worst["supplier_id"]]["name"]
        return (
            f"Most delays are tied to {supplier_name} with on-time rate {worst['on_time_rate']:.0%} "
            f"and average delay {worst['avg_delay_days']} days."
        )
    if "eta" in normalized or "lead time" in normalized:
        return "Average lead time for alternative suppliers ranges from 22 to 35 days based on current data."
    return (
        "Ask about supplier performance, delays, or lead times. Example: 'Which supplier has the most delays?'"
    )


@dataclass
class RagResult:
    answer: str
    sources: List[str]


@dataclass
class LlmResponse:
    answer: str
    supplier_ids: List[str]
    shipment_ids: List[str]


def build_rag_corpus(
    suppliers: List[Dict[str, Any]],
    shipments: List[Dict[str, Any]],
    performance: List[Dict[str, Any]],
    news: List[Dict[str, Any]],
) -> List[Tuple[str, str]]:
    documents: List[Tuple[str, str]] = []
    for item in suppliers:
        content = (
            f"Supplier {item['name']} ({item['supplier_id']}) in {item['country']} "
            f"category {item['category']} lead time {item['lead_time_days']} days "
            f"performance score {item['performance_score']}."
        )
        documents.append((f"supplier:{item['supplier_id']}", content))
    for item in shipments:
        content = (
            f"Shipment {item['shipment_id']} from supplier {item['supplier_id']} "
            f"origin {item['origin_port']} to {item['destination_port']} "
            f"planned ETA {item['planned_eta']} actual ETA {item['actual_eta']} "
            f"status {item['status']} delay reason {item['delay_reason']}."
        )
        documents.append((f"shipment:{item['shipment_id']}", content))
    for item in performance:
        content = (
            f"Performance for supplier {item['supplier_id']} on-time rate {item['on_time_rate']:.0%} "
            f"average delay {item['avg_delay_days']} days last quarter score {item['last_quarter_score']}."
        )
        documents.append((f"performance:{item['supplier_id']}", content))
    for item in news:
        content = (
            f"News {item['id']} headline {item['headline']} impact {item['impact']} "
            f"affected countries {', '.join(item['affected_countries'])} severity {item['severity']} "
            f"summary {item['summary']}."
        )
        documents.append((f"news:{item['id']}", content))
    return documents


def retrieve_context(question: str, documents: List[Tuple[str, str]], top_k: int = 3) -> List[Tuple[str, str]]:
    corpus_text = [doc[1] for doc in documents]
    vectorizer = TfidfVectorizer(stop_words="english")
    doc_vectors = vectorizer.fit_transform(corpus_text)
    query_vector = vectorizer.transform([question])
    scores = cosine_similarity(query_vector, doc_vectors).flatten()
    ranked_indices = scores.argsort()[::-1][:top_k]
    return [documents[idx] for idx in ranked_indices]


def is_alternative_request(question: str) -> bool:
    normalized = question.lower()
    triggers = [
        "alternative",
        "alternatives",
        "replace",
        "replacement",
        "substitute",
        "away from",
        "outside china",
        "non-china",
        "diversify",
    ]
    return any(trigger in normalized for trigger in triggers)


def retrieve_context_for_question(
    question: str,
    documents: List[Tuple[str, str]],
    suppliers: List[Dict[str, Any]],
    news: List[Dict[str, Any]],
) -> List[Tuple[str, str]]:
    if not is_alternative_request(question):
        return retrieve_context(question, documents)
    doc_map = {doc_id: content for doc_id, content in documents}
    retrieved: List[Tuple[str, str]] = []
    for supplier in suppliers:
        if supplier["country"].lower() != "china":
            doc_id = f"supplier:{supplier['supplier_id']}"
            if doc_id in doc_map:
                retrieved.append((doc_id, doc_map[doc_id]))
    for item in news:
        if "trade block" in item["headline"].lower():
            doc_id = f"news:{item['id']}"
            if doc_id in doc_map:
                retrieved.append((doc_id, doc_map[doc_id]))
    return retrieved or retrieve_context(question, documents)


def rag_generate_answer(
    question: str,
    suppliers: Dict[str, Dict[str, Any]],
    shipments: Dict[str, Dict[str, Any]],
    performance: Dict[str, Dict[str, Any]],
    retrieved: List[Tuple[str, str]],
) -> RagResult:
    normalized = question.lower()
    sources = [doc_id for doc_id, _ in retrieved]
    shipment_matches = re.findall(r"\bSHP-\d{4}\b", question.upper())
    digit_matches = re.findall(r"\b(\d{4})\b", question)
    if digit_matches:
        shipment_matches.extend([f"SHP-{digits}" for digits in digit_matches])
    shipment_matches = list(dict.fromkeys(shipment_matches))
    if shipment_matches:
        unknown = [shipment_id for shipment_id in shipment_matches if shipment_id not in shipments]
        if unknown:
            known_shipments = ", ".join(sorted(shipments.keys()))
            return RagResult(
                answer=(
                    f"I do not have data for {', '.join(unknown)}. "
                    f"Did you mean one of these shipments: {known_shipments}? "
                    "You can ask, for example: 'What is the status of SHP-1002?'."
                ),
                sources=sources,
            )
    if "shp-" in normalized or "shipment" in normalized:
        shipment_id = next((token.upper() for token in question.split() if token.upper().startswith("SHP-")), "")
        if shipment_id and shipment_id in shipments:
            shipment = shipments[shipment_id]
            planned = datetime.strptime(shipment["planned_eta"], "%Y-%m-%d")
            actual = datetime.strptime(shipment["actual_eta"], "%Y-%m-%d")
            delay_days = (actual - planned).days
            supplier = suppliers[shipment["supplier_id"]]["name"]
            answer = (
                f"{shipment_id} is expected to arrive {delay_days} days after the planned ETA. "
                f"Status is {shipment['status']} with delay reason '{shipment['delay_reason']}'. "
                f"Supplier: {supplier}."
            )
            return RagResult(answer=answer, sources=sources)
    if "delay" in normalized:
        worst = min(performance.values(), key=lambda item: item["on_time_rate"])
        supplier_name = suppliers[worst["supplier_id"]]["name"]
        answer = (
            f"Delays are concentrated with {supplier_name} (on-time rate {worst['on_time_rate']:.0%}, "
            f"average delay {worst['avg_delay_days']} days)."
        )
        return RagResult(answer=answer, sources=sources)
    if "performance" in normalized or "score" in normalized:
        ranked = sorted(performance.values(), key=lambda item: item["last_quarter_score"], reverse=True)
        top = ranked[0]
        supplier_name = suppliers[top["supplier_id"]]["name"]
        answer = (
            f"Top performance is {supplier_name} with score {top['last_quarter_score']} "
            f"and on-time rate {top['on_time_rate']:.0%}."
        )
        return RagResult(answer=answer, sources=sources)
    if "lead time" in normalized or "eta" in normalized:
        answer = "Alternative supplier lead times range from 22–35 days based on the synthetic dataset."
        return RagResult(answer=answer, sources=sources)
    return RagResult(
        answer=(
            "Ask about shipment delays (e.g., 'How much delay for SHP-1002?'), supplier performance, "
            "or lead times."
        ),
        sources=sources,
    )


def _post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request_obj = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request_obj, timeout=LOCAL_LLM_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def initialize_local_llm() -> None:
    global _LLM_BOOTED, _LLM_BOOT_ERROR
    if _LLM_BOOTED:
        return
    try:
        payload = {
            "model": LOCAL_LLM_MODEL,
            "messages": [{"role": "user", "content": "Respond with OK."}],
            "max_tokens": 5,
            "temperature": 0,
        }
        _post_json(f"{LOCAL_LLM_BASE_URL}/v1/chat/completions", payload)
        _LLM_BOOTED = True
        _LLM_BOOT_ERROR = ""
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as exc:
        _LLM_BOOTED = False
        _LLM_BOOT_ERROR = str(exc)


def build_llm_prompt(question: str, retrieved: List[Tuple[str, str]]) -> List[Dict[str, str]]:
    context_lines = ["Context snippets (RAG):"]
    for doc_id, content in retrieved:
        context_lines.append(f"- {doc_id}: {content}")
    context_block = "\n".join(context_lines)
    return [
        {
            "role": "system",
            "content": (
                "You are a supply chain risk analyst. Use the provided context to answer clearly and "
                "concisely. Only use facts that appear in the context. If the context is insufficient, "
                "say so. When referencing shipments or suppliers, use their IDs (e.g., SHP-1002, SUP-CHN-001). "
                "Do not invent names or IDs. Respond ONLY as JSON with keys: answer, supplier_ids, shipment_ids."
            ),
        },
        {
            "role": "user",
            "content": f"{context_block}\n\nQuestion: {question}",
        },
    ]


def call_local_llm(question: str, retrieved: List[Tuple[str, str]]) -> str:
    if not question.strip():
        return ""
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": build_llm_prompt(question, retrieved),
        "temperature": 0.2,
        "max_tokens": 320,
    }
    response = _post_json(f"{LOCAL_LLM_BASE_URL}/v1/chat/completions", payload)
    return response["choices"][0]["message"]["content"].strip()


def parse_llm_response(raw_text: str) -> LlmResponse:
    text = raw_text.strip()
    if not text.startswith("{"):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in LLM response")
        text = match.group(0)
    data = json.loads(text)
    answer = str(data.get("answer", "")).strip()
    supplier_ids = [str(item) for item in data.get("supplier_ids", []) if item]
    shipment_ids = [str(item) for item in data.get("shipment_ids", []) if item]
    if not answer:
        raise ValueError("Empty LLM answer")
    return LlmResponse(answer=answer, supplier_ids=supplier_ids, shipment_ids=shipment_ids)


def extract_capitalized_phrases(text: str) -> List[str]:
    return re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", text)


def build_allowed_phrases_from_context(retrieved: List[Tuple[str, str]]) -> set[str]:
    allowed: set[str] = set()
    for _, content in retrieved:
        allowed.update(extract_capitalized_phrases(content))
    return allowed


def build_allowed_phrases_from_data(
    suppliers: Dict[str, Dict[str, Any]],
    shipments: Dict[str, Dict[str, Any]],
    performance: Dict[str, Dict[str, Any]],
    news: List[Dict[str, Any]],
) -> set[str]:
    allowed: set[str] = set()
    for item in suppliers.values():
        allowed.add(item["name"])
        allowed.add(item["country"])
    for item in shipments.values():
        allowed.add(item["origin_port"])
        allowed.add(item["destination_port"])
    for item in performance.values():
        supplier_id = item["supplier_id"]
        if supplier_id in suppliers:
            allowed.add(suppliers[supplier_id]["name"])
    for item in news:
        allowed.update(extract_capitalized_phrases(item["headline"]))
        allowed.update(item.get("affected_countries", []))
    return allowed


def validate_llm_answer(
    llm_response: LlmResponse,
    suppliers: Dict[str, Dict[str, Any]],
    shipments: Dict[str, Dict[str, Any]],
    performance: Dict[str, Dict[str, Any]],
    news: List[Dict[str, Any]],
    retrieved: List[Tuple[str, str]],
) -> None:
    supplier_ids = set(suppliers.keys())
    shipment_ids = set(shipments.keys())
    for item in llm_response.supplier_ids:
        if item not in supplier_ids:
            raise ValueError(f"Unknown supplier id {item}")
    for item in llm_response.shipment_ids:
        if item not in shipment_ids:
            raise ValueError(f"Unknown shipment id {item}")
    for item in re.findall(r"\bSUP-[A-Z]{3}-\d{3}\b", llm_response.answer):
        if item not in supplier_ids:
            raise ValueError(f"Unknown supplier id in answer {item}")
    for item in re.findall(r"\bSHP-\d{4}\b", llm_response.answer):
        if item not in shipment_ids:
            raise ValueError(f"Unknown shipment id in answer {item}")
    allowed_phrases = build_allowed_phrases_from_context(retrieved)
    allowed_phrases |= build_allowed_phrases_from_data(suppliers, shipments, performance, news)
    unexpected_phrases = set(extract_capitalized_phrases(llm_response.answer)) - allowed_phrases
    if unexpected_phrases:
        raise ValueError(f"Unexpected named entities: {', '.join(sorted(unexpected_phrases))}")


def render_llm_answer(llm_response: LlmResponse, suppliers: Dict[str, Dict[str, Any]]) -> str:
    answer = llm_response.answer
    for supplier_id in llm_response.supplier_ids:
        if supplier_id in suppliers:
            name = suppliers[supplier_id]["name"]
            answer = answer.replace(supplier_id, f"{name} ({supplier_id})")
    return answer


initialize_local_llm()


@app.route("/", methods=["GET", "POST"])
def dashboard() -> str:
    if not _LLM_BOOTED:
        initialize_local_llm()
    news = load_json("news.json")
    suppliers = load_json("suppliers.json")
    shipments = load_json("shipments.json")
    performance = load_json("performance.json")

    suppliers_by_id = index_by(suppliers, "supplier_id")
    performance_by_id = index_by(performance, "supplier_id")
    shipments_by_id = index_by(shipments, "shipment_id")

    scenario = build_trade_block_scenario(news)
    alerts = generate_risk_alerts(shipments, suppliers_by_id, scenario)
    alternatives = suggest_alternatives(suppliers, "electronics", scenario["affected_countries"])
    shipment_summary = summarize_shipments(shipments)

    answer = ""
    question = ""
    sources: List[str] = []
    if request.method == "POST":
        question = request.form.get("question", "")
        documents = build_rag_corpus(suppliers, shipments, performance, news)
        retrieved = retrieve_context_for_question(question, documents, suppliers, news)
        try:
            raw_response = call_local_llm(question, retrieved)
            llm_response = parse_llm_response(raw_response)
            validate_llm_answer(
                llm_response,
                suppliers_by_id,
                shipments_by_id,
                performance_by_id,
                news,
                retrieved,
            )
            answer = render_llm_answer(llm_response, suppliers_by_id)
            sources = [doc_id for doc_id, _ in retrieved]
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError, KeyError, json.JSONDecodeError):
            rag_result = rag_generate_answer(
                question,
                suppliers_by_id,
                shipments_by_id,
                performance_by_id,
                retrieved,
            )
            answer = rag_result.answer
            sources = rag_result.sources

    return render_template(
        "dashboard.html",
        scenario=scenario,
        alerts=alerts,
        alternatives=alternatives,
        shipments=shipments,
        suppliers=suppliers,
        shipment_summary=shipment_summary,
        question=question,
        answer=answer,
        sources=sources,
        generated_at=datetime.utcnow(),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
