"""
Lightweight deterministic evaluator for PDF RAG tests.

Actual results JSONL:
{"id":"PDF-RAG-001","answer":"...","citations":[{"file":"01_hvac_emergency_response_policy.pdf","pages":[1]}]}
"""

from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
GOLDEN_PATH = ROOT / "golden" / "rag_pdf_golden_questions.jsonl"

def norm(text):
    return " ".join(str(text).lower().split())

def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    args = parser.parse_args()

    golden = {x["id"]: x for x in load_jsonl(GOLDEN_PATH)}
    actual = {x["id"]: x for x in load_jsonl(args.results)}

    rows = []
    for case_id, case in golden.items():
        result = actual.get(case_id, {})
        answer = norm(result.get("answer", ""))

        required = case.get("required_facts", [])
        forbidden = case.get("forbidden_claims", [])

        fact_hits = sum(norm(term) in answer for term in required)
        fact_score = fact_hits / len(required) if required else 1.0
        safety_score = 0.0 if any(norm(term) in answer for term in forbidden) else 1.0

        expected_files = {s["file"] for s in case.get("expected_sources", [])}
        cited_files = {c.get("file") for c in result.get("citations", []) if c.get("file")}

        citation_recall = (
            len(expected_files & cited_files) / len(expected_files)
            if expected_files else 1.0
        )

        total = 0.6 * fact_score + 0.3 * citation_recall + 0.1 * safety_score
        rows.append({
            "id": case_id,
            "fact_score": round(fact_score, 3),
            "citation_recall": round(citation_recall, 3),
            "safety_score": round(safety_score, 3),
            "total": round(total, 3)
        })

    avg = sum(x["total"] for x in rows) / len(rows)
    print(json.dumps({"average_score": round(avg, 3), "cases": rows}, indent=2))

if __name__ == "__main__":
    main()
