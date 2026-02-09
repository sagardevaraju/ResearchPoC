from __future__ import annotations

import json
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


@dataclass
class RiskAlert:
    shipment_id: str
    supplier: str
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


def rag_generate_answer(
    question: str,
    suppliers: Dict[str, Dict[str, Any]],
    shipments: Dict[str, Dict[str, Any]],
    performance: Dict[str, Dict[str, Any]],
    retrieved: List[Tuple[str, str]],
) -> RagResult:
    normalized = question.lower()
    sources = [doc_id for doc_id, _ in retrieved]
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


@app.route("/", methods=["GET", "POST"])
def dashboard() -> str:
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
        retrieved = retrieve_context(question, documents)
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
        shipment_summary=shipment_summary,
        question=question,
        answer=answer,
        sources=sources,
        generated_at=datetime.utcnow(),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
