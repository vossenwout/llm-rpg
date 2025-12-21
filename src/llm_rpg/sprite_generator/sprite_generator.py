from abc import ABC, abstractmethod
from pathlib import Path
import random
import time
from typing import Optional, Tuple

import pygame
import torch
from diffusers import (
    StableDiffusionPipeline,
    AutoencoderKL,
    LCMScheduler,
    EulerAncestralDiscreteScheduler,
)
import unfake
from PIL import Image
from llm_rpg.systems.battle.enemy import Enemy


class SpriteGenerator(ABC):
    @abstractmethod
    def generate_sprite(self, enemy: Enemy) -> pygame.Surface: ...


class DummySpriteGenerator(SpriteGenerator):
    def __init__(self, latency_seconds: float = 0.0):
        self.latency_seconds = latency_seconds
        self._cache: dict[str, pygame.Surface] = {}
        self._sprites_dir = Path(__file__).parent / "dummy_sprites"
        self._sprite_paths = list(self._sprites_dir.glob("*.png"))

    def generate_sprite(self, enemy: Enemy) -> pygame.Surface:
        if not self._sprite_paths:
            raise ValueError("No dummy sprites found")

        sprite_path = random.choice(self._sprite_paths)
        cache_key = sprite_path.name
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if self.latency_seconds > 0:
            time.sleep(self.latency_seconds)

        surface = pygame.image.load(sprite_path.as_posix()).convert_alpha()
        self._cache[cache_key] = surface
        return surface


class SDSpriteGenerator(SpriteGenerator):
    def __init__(
        self,
        base_model: str,
        lora_path: str,
        trigger_prompt: str,
        lcm_lora_path: Optional[str] = None,
        guidance_scale: float = 7,
        num_inference_steps: int = 20,
        inference_height: int = 512,
        inference_width: int = 512,
        vae_path: Optional[str] = None,
        use_lcm: bool = False,
        negative_prompt: Optional[str] = None,
    ):
        self.base_model = base_model
        self.lora_path = lora_path
        self.trigger_prompt = trigger_prompt
        self.lcm_lora_path = lcm_lora_path
        self.guidance_scale = guidance_scale
        self.num_inference_steps = num_inference_steps
        self.inference_height = inference_height
        self.inference_width = inference_width
        self.vae_path = vae_path
        self.use_lcm = use_lcm
        self.negative_prompt = negative_prompt
        self.device = self._get_device()

    def _get_device(self) -> str:
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _clean_sprite(self, sprite: Image.Image) -> Image.Image:
        result = unfake.process_image_sync(sprite, transparent_background=True)
        return result["image"]

    def _pil_to_surface(self, sprite: Image.Image) -> pygame.Surface:
        rgba_sprite = sprite.convert("RGBA")
        size: Tuple[int, int] = rgba_sprite.size
        surface = pygame.image.frombuffer(rgba_sprite.tobytes(), size, "RGBA")
        return surface.convert_alpha()

    def generate_sprite(self, enemy: Enemy) -> pygame.Surface:
        pipe = StableDiffusionPipeline.from_single_file(
            self.base_model,
            torch_dtype=torch.float16,
        )
        if self.vae_path:
            vae = AutoencoderKL.from_pretrained(
                self.vae_path, torch_dtype=torch.float16
            )
            pipe.vae = vae

        if self.use_lcm and self.lcm_lora_path:
            pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
        else:
            pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(
                pipe.scheduler.config
            )

        pipe.to(self.device)

        if self.use_lcm and self.lcm_lora_path:
            pipe.load_lora_weights(self.lora_path, adapter_name="style")
            pipe.load_lora_weights(self.lcm_lora_path, adapter_name="lcm")
            pipe.set_adapters(["style", "lcm"], adapter_weights=[1.0, 1.0])
        else:
            pipe.load_lora_weights(self.lora_path)
        # dummy prompt for now
        prompt = self.trigger_prompt + " " + "naruto"
        sprite = pipe(
            prompt,
            num_inference_steps=self.num_inference_steps,
            guidance_scale=self.guidance_scale,
            num_images_per_prompt=1,
            negative_prompt=self.negative_prompt,
            height=self.inference_height,
            width=self.inference_width,
            safety_checker=None,
        ).images[0]
        sprite = self._clean_sprite(sprite)
        return self._pil_to_surface(sprite)
