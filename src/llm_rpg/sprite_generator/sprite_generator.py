from abc import ABC, abstractmethod
from pathlib import Path
import time

import pygame


class SpriteGenerator(ABC):
    @abstractmethod
    def generate_sprite(self, prompt: str) -> pygame.Surface: ...


class DummySpriteGenerator(SpriteGenerator):
    def __init__(self, latency_seconds: float = 0.0):
        self.latency_seconds = latency_seconds
        self._cache: dict[str, pygame.Surface] = {}
        self._sprites_dir = Path(__file__).parent / "dummy_sprites"

    def generate_sprite(self, prompt: str) -> pygame.Surface:
        key = prompt.strip().lower()
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        filename = key.replace(" ", "_") + ".png"
        sprite_path = self._sprites_dir / filename
        if not sprite_path.exists():
            raise ValueError(f"Unknown dummy sprite: {prompt}")

        if self.latency_seconds > 0:
            time.sleep(self.latency_seconds)

        surface = pygame.image.load(sprite_path.as_posix()).convert_alpha()
        self._cache[key] = surface
        return surface
