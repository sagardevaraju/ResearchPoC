from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, render_template, request

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


@app.route("/", methods=["GET", "POST"])
def dashboard() -> str:
    news = load_json("news.json")
    suppliers = load_json("suppliers.json")
    shipments = load_json("shipments.json")
    performance = load_json("performance.json")

    suppliers_by_id = index_by(suppliers, "supplier_id")
    performance_by_id = index_by(performance, "supplier_id")

    scenario = build_trade_block_scenario(news)
    alerts = generate_risk_alerts(shipments, suppliers_by_id, scenario)
    alternatives = suggest_alternatives(suppliers, "electronics", scenario["affected_countries"])
    shipment_summary = summarize_shipments(shipments)

    answer = ""
    question = ""
    if request.method == "POST":
        question = request.form.get("question", "")
        answer = answer_question(question, suppliers_by_id, performance_by_id)

    return render_template(
        "dashboard.html",
        scenario=scenario,
        alerts=alerts,
        alternatives=alternatives,
        shipments=shipments,
        shipment_summary=shipment_summary,
        question=question,
        answer=answer,
        generated_at=datetime.utcnow(),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
