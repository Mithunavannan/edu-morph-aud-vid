# src/utils/validators.py
def require_text(text: str, min_len=10):
    if not text or len(text.strip()) < min_len:
        raise ValueError(f"Input text is too short. Need at least {min_len} chars.")
    return text.strip()

def clamp(x, lo, hi):
    return max(lo, min(hi, x))
