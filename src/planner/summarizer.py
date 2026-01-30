# src/planner/summarizer.py
import math
import re
from collections import Counter

def _sent_tokenize(text: str) -> list[str]:
    # simple sentence split
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sents if len(s.strip()) > 10]

def _word_tokenize(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]+", text.lower())
    return words

def extractive_summary(text: str, max_sentences=6) -> str:
    """
    Simple TF scoring of sentences. Good enough for prototype.
    """
    sents = _sent_tokenize(text)
    if not sents:
        return text[:500]

    words = _word_tokenize(text)
    freq = Counter(words)

    def sent_score(s: str) -> float:
        w = _word_tokenize(s)
        if not w:
            return 0.0
        return sum(freq[x] for x in w) / math.sqrt(len(w))

    ranked = sorted([(sent_score(s), i, s) for i, s in enumerate(sents)], reverse=True)
    top = sorted(ranked[:max_sentences], key=lambda x: x[1])
    return " ".join([x[2] for x in top]).strip()

def bullet_points_from_summary(summary: str, max_points=8) -> list[str]:
    # split by sentences and convert to bullets
    sents = _sent_tokenize(summary)
    pts = sents[:max_points]
    return [p.strip() for p in pts]
