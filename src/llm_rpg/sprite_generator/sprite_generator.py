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
from llm_rpg.llm.llm import LLM


class SpriteGenerator(ABC):
    @abstractmethod
    def generate_sprite(self, enemy: Enemy) -> pygame.Surface: ...


def _clean_sprite(sprite: Image.Image) -> Image.Image:
    result = unfake.process_image_sync(sprite, transparent_background=True)
    return result["image"]


def _pil_to_surface(sprite: Image.Image) -> pygame.Surface:
    rgba_sprite = sprite.convert("RGBA")
    size: Tuple[int, int] = rgba_sprite.size
    surface = pygame.image.frombuffer(rgba_sprite.tobytes(), size, "RGBA")
    return surface.convert_alpha()


class DummySpriteGenerator(SpriteGenerator):
    def __init__(self, latency_seconds: float = 0.0):
        self.latency_seconds = latency_seconds
        self._cache: dict[str, pygame.Surface] = {}
        self._sprites_dir = Path(__file__).parent / "dummy_sprites"
        self._sprite_paths = list(self._sprites_dir.glob("*devil_dog.png"))

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

        with Image.open(sprite_path) as raw_sprite:
            cleaned_sprite = _clean_sprite(raw_sprite.convert("RGBA"))
        surface = _pil_to_surface(cleaned_sprite)
        self._cache[cache_key] = surface
        return surface


class SDSpriteGenerator(SpriteGenerator):
    def __init__(
        self,
        base_model: str,
        lora_path: str,
        trigger_prompt: str,
        prompt_llm: LLM,
        prompt_template: str,
        lcm_lora_path: Optional[str] = None,
        guidance_scale: float = 7,
        num_inference_steps: int = 20,
        inference_height: int = 512,
        inference_width: int = 512,
        vae_path: Optional[str] = None,
        use_lcm: bool = False,
        negative_prompt: Optional[str] = None,
        debug: bool = False,
    ):
        self.base_model = base_model
        self.lora_path = lora_path
        self.trigger_prompt = trigger_prompt
        self.prompt_llm = prompt_llm
        self.prompt_template = prompt_template
        self.lcm_lora_path = lcm_lora_path
        self.guidance_scale = guidance_scale
        self.num_inference_steps = num_inference_steps
        self.inference_height = inference_height
        self.inference_width = inference_width
        self.vae_path = vae_path
        self.use_lcm = use_lcm
        self.negative_prompt = negative_prompt
        self.debug = debug
        self.device = self._get_device()

    def _get_device(self) -> str:
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _build_sprite_prompt(self, enemy: Enemy) -> str:
        attempts = 0
        while attempts < 3:
            prompt = self.prompt_template.format(
                enemy_name=enemy.name, enemy_description=enemy.description
            )
            try:
                if self.debug:
                    print("////////////DEBUG SpritePrompt LLM prompt////////////")
                    print(prompt)
                    print("////////////DEBUG SpritePrompt LLM prompt////////////")
                output = self.prompt_llm.generate_completion(prompt=prompt)
                if self.debug:
                    print("////////////DEBUG SpritePrompt LLM response////////////")
                    print(output)
                    print("////////////DEBUG SpritePrompt LLM response////////////")
                return output.strip()
            except Exception:
                attempts += 1
        return enemy.description

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
        sprite_prompt = self._build_sprite_prompt(enemy)
        prompt = f"{self.trigger_prompt}, {sprite_prompt}"
        if self.debug:
            print("////////////DEBUG Diffusion prompt////////////")
            print(prompt)
            print("////////////DEBUG Diffusion prompt////////////")
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
        sprite = _clean_sprite(sprite)
        return _pil_to_surface(sprite)
