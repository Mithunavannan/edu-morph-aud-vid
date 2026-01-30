# src/planner/prompt_builder.py
from dataclasses import dataclass

@dataclass
class PromptPack:
    prompt: str
    negative_prompt: str

DEFAULT_NEG = (
    "low quality, blurry, noisy, deformed, bad anatomy, extra fingers, distorted face, watermark, text, logo"
)

def build_prompt(output_type: str, topic: str, content_hint: str) -> PromptPack:
    output_type = output_type.lower().strip()

    if output_type == "summary_image":
        prompt = (
            f"Educational summary poster image about {topic}. "
            f"Clean layout, infographic style, minimal, high clarity. "
            f"Key points: {content_hint}"
        )
    elif output_type == "comic":
        prompt = (
            f"4 panel educational comic about {topic}. "
            f"Simple characters, clean line art, colorful, clear expressions. "
            f"Story: {content_hint}"
        )
    elif output_type == "flowchart":
        prompt = (
            f"Flowchart style infographic about {topic}. "
            f"Minimal clean design, nodes and arrows, readable. "
            f"Steps: {content_hint}"
        )
    elif output_type == "mindmap":
        prompt = (
            f"Mind map infographic about {topic}. "
            f"Central idea with branches, clean, minimal, high readability. "
            f"Concepts: {content_hint}"
        )
    elif output_type == "realistic":
        prompt = (
            f"Ultra realistic photo of {content_hint}. "
            f"High detail, DSLR, sharp focus, cinematic lighting."
        )
    elif output_type == "video_scene":
        prompt = (
            f"Educational infographic illustration about {topic}. "
            f"Clean minimal design, high clarity. "
            f"Caption idea: {content_hint}"
        )
    else:
        prompt = f"Educational illustration about {topic}. {content_hint}"

    return PromptPack(prompt=prompt, negative_prompt=DEFAULT_NEG)
