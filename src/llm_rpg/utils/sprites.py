import json
from pathlib import Path
import pygame

from llm_rpg.utils.assets import asset_file


class SpriteSheet:
    def __init__(self, atlas_relative_json: str):
        with asset_file(atlas_relative_json) as atlas_path:
            with open(atlas_path, "r", encoding="utf-8") as f:
                atlas = json.load(f)

        meta_image = atlas["meta"]["image"]

        with asset_file(Path(atlas_relative_json).parent / meta_image) as image_path:
            self.image = pygame.image.load(image_path).convert_alpha()

        self.frames = {}
        for frame in atlas.get("frames", []):
            name = frame.get("filename")
            frame_rect = frame["frame"]
            subsurface = self.image.subsurface(
                pygame.Rect(
                    frame_rect["x"], frame_rect["y"], frame_rect["w"], frame_rect["h"]
                )
            )

            if frame.get("trimmed"):
                src_size = frame["sourceSize"]
                sprite_src = frame["spriteSourceSize"]
                full_surface = pygame.Surface(
                    (src_size["w"], src_size["h"]), pygame.SRCALPHA
                )
                full_surface.blit(
                    subsurface,
                    (sprite_src["x"], sprite_src["y"]),
                )
                self.frames[name] = full_surface
            else:
                self.frames[name] = subsurface

    def get(self, name: str) -> pygame.Surface:
        return self.frames[name]

    def get_scaled(self, name: str, scale: float) -> pygame.Surface:
        sprite = self.get(name)
        return pygame.transform.scale_by(sprite, scale)
