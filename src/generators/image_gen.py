# src/generators/image_gen.py
import torch
from diffusers import StableDiffusionXLPipeline
from pathlib import Path

class SDXLImageGenerator:
    def __init__(
        self,
        model_id="stabilityai/stable-diffusion-xl-base-1.0",
        device="cuda",
        use_fp16=True
    ):
        dtype = torch.float16 if use_fp16 and device == "cuda" else torch.float32
        self.pipe = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype
        )
        if device == "cuda":
            self.pipe = self.pipe.to("cuda")
            # memory optimizations
            try:
                self.pipe.enable_xformers_memory_efficient_attention()
            except Exception:
                pass
            self.pipe.enable_attention_slicing()
        else:
            self.pipe = self.pipe.to("cpu")

    @torch.inference_mode()
    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 768,
        height: int = 768,
        steps: int = 25,
        guidance: float = 7.0,
        seed: int | None = None,
        out_path: str | Path = "output.png"
    ) -> str:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        gen = None
        if seed is not None:
            gen = torch.Generator(device="cuda").manual_seed(seed)

        img = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=steps,
            guidance_scale=guidance,
            generator=gen
        ).images[0]

        img.save(out_path)
        return str(out_path)
