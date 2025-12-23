from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import random
from typing import Protocol

import pygame


class BattleBackground(Protocol):
    def update(self, dt: float) -> None: ...

    def render(self, screen: pygame.Surface) -> None: ...


@dataclass(frozen=True)
class BattleBackgroundConfig:
    base_width: int
    base_height: int
    speed_multiplier: float


def build_battle_background(
    enemy_name: str,
    config: BattleBackgroundConfig,
) -> BattleBackground:
    seed = _hash_seed(enemy_name)
    rng = random.Random(seed)
    effect = rng.choice(
        [
            DiamondBandedBackground,
        ]
    )
    palette = rng.choice(effect.palettes)
    return effect(
        base_size=(config.base_width, config.base_height),
        palette=palette,
        seed=seed,
        speed_multiplier=config.speed_multiplier,
    )


def _hash_seed(name: str) -> int:
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


_DIAMOND_PALETTES: list[list[tuple[int, int, int]]] = [
    [(226, 158, 82), (238, 186, 98), (194, 146, 92), (212, 168, 130)],
    [(216, 64, 112), (236, 96, 136), (192, 56, 96), (168, 88, 160)],
    [(236, 200, 96), (216, 184, 72), (184, 216, 120), (156, 196, 112)],
    [(168, 112, 184), (188, 144, 204), (112, 176, 136), (96, 152, 120)],
    [(96, 136, 216), (120, 160, 232), (152, 128, 216), (128, 112, 196)],
]


class _BaseBackground:
    def __init__(
        self,
        base_size: tuple[int, int],
        palette: list[tuple[int, int, int]],
        seed: int,
        speed_multiplier: float,
    ) -> None:
        self.base_size = base_size
        self.palette = palette
        self.seed = seed
        self.speed_multiplier = speed_multiplier
        self.time = 0.0
        self.surface = pygame.Surface(base_size)
        self.surface_converted = False

    def update(self, dt: float) -> None:
        self.time += dt * self.speed_multiplier

    def render(self, screen: pygame.Surface) -> None:
        if pygame.display.get_surface() is not None and not self.surface_converted:
            self.surface = self.surface.convert()
            self.surface_converted = True
        self._render_to_surface(self.surface)
        screen_size = screen.get_size()
        if screen_size == self.base_size:
            screen.blit(self.surface, (0, 0))
            return
        scaled = pygame.transform.scale(self.surface, screen_size)
        screen.blit(scaled, (0, 0))

    def _render_to_surface(self, surface: pygame.Surface) -> None:
        raise NotImplementedError


class DiamondBandedBackground(_BaseBackground):
    palettes = _DIAMOND_PALETTES

    def __init__(
        self,
        base_size: tuple[int, int],
        palette: list[tuple[int, int, int]],
        seed: int,
        speed_multiplier: float,
    ) -> None:
        super().__init__(
            base_size=base_size,
            palette=palette,
            seed=seed,
            speed_multiplier=speed_multiplier,
        )
        rng = random.Random(seed ^ 0xFACE)
        self.tile = rng.randint(10, 16)
        self.shift = rng.uniform(0.8, 1.6)
        self.shift_speed = rng.uniform(0.2, 0.4)
        self.step = rng.uniform(0.3, 0.5)
        self.palette_speed = rng.uniform(0.04, 0.08)

    def _render_to_surface(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        palette = self.palette
        plen = len(palette)
        time = self.time
        tile = self.tile
        half = tile * 0.5
        shift = self.shift
        shift_speed = self.shift_speed
        step = self.step
        palette_speed = self.palette_speed
        for y in range(height):
            phase = math.sin(y * 0.06 + time * shift_speed) * shift
            palette_shift = (time * palette_speed * plen) % plen
            for x in range(width):
                dx = abs(((x + phase) % tile) - half)
                dy = abs((y % tile) - half)
                diamond = dx + dy
                step_level = int((diamond / tile + time * step) * plen) % plen
                palette_index = (step_level + palette_shift) % plen
                base_index = int(palette_index)
                next_index = (base_index + 1) % plen
                frac = palette_index - base_index
                surface.set_at(
                    (x, y),
                    _lerp_color(palette[base_index], palette[next_index], frac),
                )


def _lerp_color(
    start: tuple[int, int, int],
    end: tuple[int, int, int],
    t: float,
) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return (
        int(round(start[0] + (end[0] - start[0]) * t)),
        int(round(start[1] + (end[1] - start[1]) * t)),
        int(round(start[2] + (end[2] - start[2]) * t)),
    )
