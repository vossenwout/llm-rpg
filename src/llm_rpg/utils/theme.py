import pygame

from llm_rpg.utils.assets import asset_file


class Theme:
    def __init__(self):
        self.unit = 8
        self.scale = 3
        self.grid = self.unit * self.scale
        with asset_file("fonts/PressStart2P-Regular.ttf") as font_path:
            self.fonts = {
                "title": pygame.font.Font(font_path, 48),
                "large": pygame.font.Font(font_path, 32),
                "medium": pygame.font.Font(font_path, 24),
                "small": pygame.font.Font(font_path, 16),
            }

        self.colors = {
            "background": (8, 16, 48),
            "panel": (18, 30, 74),
            "panel_inner": (12, 22, 60),
            "primary": (92, 188, 255),
            "text": (240, 244, 252),
            "text_selected": (255, 230, 92),
            "text_hint": (164, 188, 220),
            "border_dark": (28, 52, 96),
            "border_light": (176, 220, 255),
        }

    def spacing(self, units: float) -> int:
        return int(self.grid * units)
