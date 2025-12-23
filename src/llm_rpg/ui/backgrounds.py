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
            # DiamondBandedBackground,
            # VCRGlitchBackground,
            PlasmaRippleBackground,
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


_COLOR_PALLETES: list[list[tuple[int, int, int]]] = [
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
    palettes = _COLOR_PALLETES

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


class VCRGlitchBackground(_BaseBackground):
    palettes = _COLOR_PALLETES

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
        rng = random.Random(seed ^ 0xC0FFEE)
        self.scanline_speed = rng.uniform(1.6, 2.4)
        self.scanline_intensity = rng.uniform(0.12, 0.2)
        self.noise_intensity = rng.uniform(3.0, 8.0)
        self.drift_speed = rng.uniform(0.5, 0.9)
        self.drift_amount = rng.uniform(3.0, 6.0)
        self.chroma_amount = rng.uniform(12.0, 20.0)
        self.tear_speed = rng.uniform(0.35, 0.6)
        self.tear_height = rng.uniform(6.0, 12.0)

    def _render_to_surface(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        palette = self.palette
        plen = len(palette)
        time = self.time
        scanline_speed = self.scanline_speed
        scanline_intensity = self.scanline_intensity
        noise_intensity = self.noise_intensity
        drift_speed = self.drift_speed
        drift_amount = self.drift_amount
        chroma_amount = self.chroma_amount
        tear_speed = self.tear_speed
        tear_height = self.tear_height
        tear_pos = (time * tear_speed * height) % height
        for y in range(height):
            y_phase = y * 0.07 + time * drift_speed
            drift = math.sin(y_phase) * drift_amount
            tear_offset = 0.0
            if abs(y - tear_pos) < tear_height:
                band = (tear_height - abs(y - tear_pos)) / tear_height
                tear_offset = (
                    math.sin(time * 12.0 + y * 0.2) * (drift_amount * 2.5) * band
                )
            scanline = 1.0 - scanline_intensity * (
                0.5 + 0.5 * math.sin(y * 0.6 + time * scanline_speed)
            )
            for x in range(width):
                nx = (x + drift + tear_offset) * 0.04
                ny = y * 0.03
                wave = 0.5 + 0.5 * math.sin(nx + ny + time * 0.8)
                palette_index = wave * (plen - 1)
                base_index = int(palette_index)
                next_index = min(base_index + 1, plen - 1)
                frac = palette_index - base_index
                base = _lerp_color(palette[base_index], palette[next_index], frac)
                chroma = chroma_amount * math.sin((x + drift) * 0.06 + time * 1.6)
                noise = (_hash_noise(x, y, int(time * 14.0), self.seed) - 0.5) * 2.0
                r = base[0] + chroma + noise * noise_intensity
                g = base[1] + noise * (noise_intensity * 0.6)
                b = base[2] - chroma + noise * (noise_intensity * 0.8)
                r = max(0, min(255, int(r * scanline)))
                g = max(0, min(255, int(g * scanline)))
                b = max(0, min(255, int(b * scanline)))
                surface.set_at((x, y), (r, g, b))


class PlasmaRippleBackground(_BaseBackground):
    palettes = _COLOR_PALLETES

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
        rng = random.Random(seed ^ 0xA1B2)
        self.wave_speed = rng.uniform(0.5, 0.95)
        self.wave_scale = rng.uniform(0.045, 0.075)
        self.wave_mix = rng.uniform(0.35, 0.65)
        self.interleave = rng.uniform(0.6, 1.4)
        self.palette_speed = rng.uniform(0.05, 0.1)
        self.band_count = rng.randint(10, 14)
        self.contrast = rng.uniform(1.25, 1.45)

    def _render_to_surface(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        palette = self.palette
        plen = len(palette)
        time = self.time
        wave_speed = self.wave_speed
        wave_scale = self.wave_scale
        wave_mix = self.wave_mix
        interleave = self.interleave
        palette_shift = (time * self.palette_speed * plen) % plen
        band_count = self.band_count
        contrast = self.contrast
        for y in range(height):
            row_dir = 1.0 if (y % 2 == 0) else -1.0
            row_shift = math.sin(time * 1.3 + y * 0.14) * interleave * row_dir
            for x in range(width):
                nx = (x + row_shift) * wave_scale
                ny = y * wave_scale
                wave_a = math.sin(nx + time * wave_speed)
                wave_b = math.sin(ny * 1.25 - time * (wave_speed * 0.8))
                wave_c = math.sin((nx + ny) * 0.85 + time * (wave_speed * 1.05))
                plasma = wave_a + wave_b * wave_mix + wave_c * (1.0 - wave_mix)
                value = _clamp01((plasma + 3.0) / 6.0)
                value = _clamp01(0.5 + (value - 0.5) * contrast)
                value = round(value * (band_count - 1)) / (band_count - 1)
                palette_index = (value * (plen - 1) + palette_shift) % plen
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


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _hash_noise(x: int, y: int, t: int, seed: int) -> float:
    n = x * 374761393 + y * 668265263 + t * 2147483647 + seed * 1442695041
    n = (n ^ (n >> 13)) * 1274126177
    n = n ^ (n >> 16)
    return (n & 0xFF) / 255.0
