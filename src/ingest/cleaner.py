# src/ingest/cleaner.py
import re

def clean_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\s+\n", "\n", text)
    text = text.strip()
    return text

def chunk_text(text: str, chunk_size=1200, overlap=120) -> list[str]:
    """
    Simple chunking by characters (fast prototype).
    overlap helps preserve context across chunks.
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+chunk_size]
        chunks.append(chunk)
        i += (chunk_size - overlap)
    return chunks
