# src/planner/scene_planner.py
import re

def plan_comic_scenes(text: str, max_scenes=4) -> list[dict]:
    """
    Converts content into a simple storyboard.
    No model. Rule-based + sentence split.
    """
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
    sents = [s.strip() for s in sents if len(s.strip()) > 15]

    scenes = []
    for i, s in enumerate(sents[:max_scenes]):
        scenes.append({
            "scene_id": i + 1,
            "visual": f"Simple educational illustration of: {s[:120]}",
            "dialogue": f"Scene {i+1}: {s[:150]}",
        })

    if not scenes:
        scenes = [{
            "scene_id": 1,
            "visual": "Simple educational illustration",
            "dialogue": "No enough text, showing a generic learning scene."
        }]
    return scenes

def plan_video_scenes(text: str, max_scenes=6) -> list[dict]:
    """
    Video storyboard scenes: title + key frames.
    """
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
    sents = [s.strip() for s in sents if len(s.strip()) > 15]

    scenes = []
    for i, s in enumerate(sents[:max_scenes]):
        scenes.append({
            "scene_id": i + 1,
            "caption": s[:160],
            "image_prompt": f"Educational infographic style, clean, minimal, about: {s[:120]}",
        })

    if not scenes:
        scenes = [{
            "scene_id": 1,
            "caption": "Overview",
            "image_prompt": "Educational infographic, clean minimal style, learning concept"
        }]
    return scenes
