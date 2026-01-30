# src/generators/video_gen.py
from pathlib import Path
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def make_video_from_images(
    image_paths: list[str],
    out_mp4: str | Path,
    fps: int = 24,
    seconds_per_image: float = 2.5,
    audio_path: str | None = None
) -> str:
    out_mp4 = Path(out_mp4)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    clips = []
    for p in image_paths:
        clip = ImageClip(p).set_duration(seconds_per_image)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")

    if audio_path:
        audio = AudioFileClip(audio_path)
        video = video.set_audio(audio)

    video.write_videofile(
        str(out_mp4),
        fps=fps,
        codec="libx264",
        audio_codec="aac" if audio_path else None
    )
    return str(out_mp4)
