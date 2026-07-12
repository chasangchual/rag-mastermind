from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus_pdfs"
GOLDEN = ROOT / "golden" / "rag_pdf_golden_questions.jsonl"

errors = []
count = 0
seen = set()

for line_no, line in enumerate(GOLDEN.read_text(encoding="utf-8").splitlines(), start=1):
    if not line.strip():
        continue
    count += 1
    case = json.loads(line)

    case_id = case["id"]
    if case_id in seen:
        errors.append(f"Duplicate case id: {case_id}")
    seen.add(case_id)

    for source in case.get("expected_sources", []):
        path = CORPUS / source["file"]
        if not path.exists():
            errors.append(f"{case_id}: missing PDF {source['file']}")
        elif path.suffix.lower() != ".pdf":
            errors.append(f"{case_id}: expected PDF file {source['file']}")

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(f"Validation passed: {count} golden cases.")
print(f"PDF corpus files: {len(list(CORPUS.glob('*.pdf')))}")
