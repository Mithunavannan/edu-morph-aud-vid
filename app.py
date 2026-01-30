import streamlit as st
from pathlib import Path
import yaml
import time

from src.ingest.pdf_reader import read_pdf_to_text
from src.ingest.cleaner import clean_text, chunk_text
from src.planner.summarizer import extractive_summary, bullet_points_from_summary
from src.planner.scene_planner import plan_comic_scenes, plan_video_scenes
from src.planner.prompt_builder import build_prompt
from src.renderers.flowchart_render import render_simple_flowchart
from src.renderers.mindmap_render import render_mindmap
from src.generators.image_gen import SDXLImageGenerator
from src.generators.voice_gen import generate_voice_piper
from src.generators.video_gen import make_video_from_images
from src.utils.file_utils import ensure_dir, save_json, make_id, safe_filename
from src.utils.validators import require_text


# --------------------------
# Load Settings
# --------------------------
CONFIG_DIR = Path("configs")
SETTINGS_PATH = CONFIG_DIR / "settings.yaml"

def load_settings():
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

settings = load_settings()

OUT_DIR = Path("outputs")
ensure_dir(OUT_DIR / "images")
ensure_dir(OUT_DIR / "audio")
ensure_dir(OUT_DIR / "videos")
ensure_dir(OUT_DIR / "json")


# --------------------------
# Lazy-load SDXL model once
# --------------------------
@st.cache_resource
def get_image_generator():
    return SDXLImageGenerator(
        model_id=settings["image"]["model_id"],
        device=settings["image"]["device"],
        use_fp16=settings["image"]["use_fp16"]
    )


# --------------------------
# UI
# --------------------------
st.set_page_config(page_title="Edu-Morph GenAI", layout="wide")

st.title("📚 Edu-Morph — Study Material → Visual Outputs (GenAI Prototype)")
st.caption("PDF/Text → Summary Image / Comic / Flowchart / Mindmap / Video + Voice (Prototype)")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Input")
    input_mode = st.radio("Select input type", ["Text", "PDF"], horizontal=True)

    text_input = ""
    uploaded_pdf = None

    if input_mode == "Text":
        text_input = st.text_area("Paste your study material", height=220)
    else:
        uploaded_pdf = st.file_uploader("Upload PDF study material", type=["pdf"])

    topic = st.text_input("Topic / Title (optional)", value="Edu-Morph Topic")

with col2:
    st.subheader("🎯 Output Type")
    output_type = st.selectbox(
        "Choose what to generate",
        ["summary_image", "comic", "flowchart", "mindmap", "video_explainer", "realistic"]
    )

    st.subheader("⚙️ Settings")
    img_size = st.selectbox("Image size", ["512x512", "768x768"], index=1)
    steps = st.slider("Diffusion steps", 10, 40, settings["image"]["steps"])
    guidance = st.slider("Guidance scale", 3.0, 12.0, float(settings["image"]["guidance_scale"]))
    seed = st.number_input("Seed (0 = random)", min_value=0, max_value=999999, value=0)

    make_voice = st.checkbox("Add voice narration (for video)", value=True)
    fps = st.slider("Video FPS", 12, 30, settings["video"]["fps"])
    seconds_per_scene = st.slider("Seconds per scene", 1.0, 5.0, float(settings["video"]["seconds_per_scene"]))

st.divider()

if st.button("🚀 Generate Output", type="primary"):
    try:
        # 1) Read input text
        if input_mode == "PDF":
            if uploaded_pdf is None:
                st.error("Please upload a PDF.")
                st.stop()

            # Save uploaded PDF
            job_id = make_id("job")
            pdf_path = Path("data/extracted_text") / f"{job_id}.pdf"
            ensure_dir(pdf_path.parent)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_pdf.read())

            raw_text = read_pdf_to_text(pdf_path)
        else:
            raw_text = text_input

        raw_text = require_text(raw_text, min_len=20)
        cleaned = clean_text(raw_text)
        chunks = chunk_text(cleaned, chunk_size=settings["text"]["chunk_size"], overlap=settings["text"]["overlap"])

        # 2) Summarize (no API)
        summary = extractive_summary(cleaned, max_sentences=settings["text"]["summary_sentences"])
        bullets = bullet_points_from_summary(summary, max_points=8)
        content_hint = " | ".join(bullets)

        # 3) Save planning JSON
        safe_topic = safe_filename(topic)
        job_id = make_id("job")

        plan_json = {
            "job_id": job_id,
            "topic": topic,
            "output_type": output_type,
            "summary": summary,
            "bullets": bullets,
            "num_chunks": len(chunks),
        }
        save_json(plan_json, OUT_DIR / "json" / f"{job_id}_plan.json")

        # 4) Generate output
        w, h = map(int, img_size.split("x"))
        seed_val = None if seed == 0 else int(seed)

        img_gen = get_image_generator()

        st.info("Generating... please wait ⏳")
        time.sleep(0.3)

        if output_type in ["summary_image", "comic", "mindmap", "flowchart", "realistic"]:
            # prompt
            pack = build_prompt(output_type, topic, content_hint)

            if output_type == "flowchart":
                # diagram-like flowchart (code-rendered)
                out_fc = render_simple_flowchart(bullets, OUT_DIR / "images" / f"{job_id}_flowchart.png")
                st.success("✅ Flowchart generated (Graphviz).")
                st.image(out_fc, use_container_width=True)

            elif output_type == "mindmap":
                # mindmap (code-rendered) using bullets grouped quickly
                branches = {
                    "Key Concepts": bullets[:3],
                    "More Points": bullets[3:6],
                    "Extras": bullets[6:],
                }
                out_mm = render_mindmap(topic, branches, OUT_DIR / "images" / f"{job_id}_mindmap.png")
                st.success("✅ Mindmap generated (NetworkX).")
                st.image(out_mm, use_container_width=True)

            else:
                # SDXL generation
                out_img = img_gen.generate(
                    prompt=pack.prompt,
                    negative_prompt=pack.negative_prompt,
                    width=w,
                    height=h,
                    steps=steps,
                    guidance=guidance,
                    seed=seed_val,
                    out_path=OUT_DIR / "images" / f"{job_id}_{output_type}.png"
                )
                st.success("✅ Image generated (SDXL).")
                st.image(out_img, use_container_width=True)
                st.code(pack.prompt, language="text")

        elif output_type == "video_explainer":
            # Plan video scenes
            scenes = plan_video_scenes(summary, max_scenes=settings["video"]["max_scenes"])
            save_json({"job_id": job_id, "scenes": scenes}, OUT_DIR / "json" / f"{job_id}_scenes.json")

            image_paths = []
            for sc in scenes:
                caption = sc["caption"]
                pack = build_prompt("video_scene", topic, caption)

                out_img = img_gen.generate(
                    prompt=pack.prompt,
                    negative_prompt=pack.negative_prompt,
                    width=w,
                    height=h,
                    steps=steps,
                    guidance=guidance,
                    seed=seed_val,
                    out_path=OUT_DIR / "images" / f"{job_id}_scene_{sc['scene_id']}.png"
                )
                image_paths.append(out_img)

            audio_path = None
            narration = f"Topic: {topic}. " + summary

            if make_voice:
                audio_path = generate_voice_piper(
                    text=narration,
                    model_path=settings["voice"]["piper_model_path"],
                    out_wav=OUT_DIR / "audio" / f"{job_id}_voice.wav"
                )

            out_video = make_video_from_images(
                image_paths=image_paths,
                out_mp4=OUT_DIR / "videos" / f"{job_id}_explainer.mp4",
                fps=fps,
                seconds_per_image=seconds_per_scene,
                audio_path=audio_path
            )

            st.success("✅ Video Explainer generated!")
            st.video(out_video)

        else:
            st.error("Unknown output type selected.")

    except Exception as e:
        st.error(f"❌ Error: {e}")
