# src/generators/voice_gen.py
import subprocess
from pathlib import Path

def generate_voice_piper(
    text: str,
    model_path: str,
    out_wav: str | Path = "voice.wav"
) -> str:
    """
    Piper is usually run via CLI:
    piper --model en_US-...onnx --output_file out.wav
    """
    out_wav = Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "piper",
        "--model", model_path,
        "--output_file", str(out_wav)
    ]

    # pass text via stdin
    p = subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True)

    if p.returncode != 0:
        raise RuntimeError(
            f"Piper TTS failed.\nSTDERR:\n{p.stderr.decode('utf-8', errors='ignore')}"
        )

    return str(out_wav)
