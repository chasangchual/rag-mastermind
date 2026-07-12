# PDF-focused RAG Golden Test Data

This package is designed specifically for testing RAG ingestion and retrieval over
PDF documents. All documents are synthetic.

## Corpus characteristics

The corpus includes:

- Text-based policy PDFs
- PDFs containing tables
- A four-page work-order history PDF
- A current-versus-archived policy conflict
- An untrusted prompt-injection document
- An image-only scanned PDF for OCR testing
- A two-column PDF for reading-order testing

## Contents

- `corpus_pdfs/`: 12 PDFs to ingest
- `golden/rag_pdf_golden_questions.jsonl`: 20 test cases
- `golden/rag_pdf_golden_questions.csv`: spreadsheet-friendly version
- `golden/sample_actual_results.jsonl`: example result format
- `schemas/pdf_golden_case.schema.json`
- `scripts/validate_pdf_golden_data.py`
- `scripts/evaluate_pdf_results.py`

## Important ingestion settings

Preserve these fields where possible:

- PDF file name
- PDF title
- Page number
- Source ID shown in the footer or document metadata
- Document status such as current, archived, or untrusted
- Effective date

For the image-only PDF
`11_scanned_equipment_inspection_note.pdf`, OCR must be enabled.

## Validate

```bash
python scripts/validate_pdf_golden_data.py
```

## Evaluate

Export actual answers as JSONL:

```json
{"id":"PDF-RAG-001","answer":"The target is 15 minutes.","citations":[{"file":"01_hvac_emergency_response_policy.pdf","pages":[1]}]}
```

Then run:

```bash
python scripts/evaluate_pdf_results.py golden/sample_actual_results.jsonl
```

## Recommended RAG metrics

- Answer correctness
- Citation file accuracy
- Citation page accuracy
- Retrieval recall@k
- Current-versus-archived document selection
- OCR success
- Multi-page table retrieval
- Prompt-injection resistance
- Unanswerable-question abstention
