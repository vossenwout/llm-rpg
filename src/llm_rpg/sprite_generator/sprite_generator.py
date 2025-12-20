from abc import ABC, abstractmethod
from pathlib import Path
import random
import time

import pygame

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
