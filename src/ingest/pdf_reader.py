# src/ingest/pdf_reader.py
from pathlib import Path
from PyPDF2 import PdfReader

def read_pdf_to_text(pdf_path: str | Path) -> str:
    pdf_path = Path(pdf_path)
    reader = PdfReader(str(pdf_path))
    pages = []
    for p in reader.pages:
        t = p.extract_text() or ""
        pages.append(t)
    return "\n".join(pages).strip()
