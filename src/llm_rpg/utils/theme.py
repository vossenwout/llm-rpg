import pygame

from llm_rpg.utils.assets import asset_file


class Theme:
    def __init__(self, scale: int = 1):
        self.unit = 8 * scale
        self.scale = scale
        with asset_file("fonts/PressStart2P-Regular.ttf") as font_path:
            self.fonts = {
                "title": pygame.font.Font(font_path, 48 * scale),
                "large": pygame.font.Font(font_path, 16 * scale),
                "medium": pygame.font.Font(font_path, 12 * scale),
                "small": pygame.font.Font(font_path, 10 * scale),
            }

        self.colors = {
            "background": (0, 0, 0),
            "panel": (255, 255, 255),
            "panel_inner": (0, 0, 0),
            "primary": (255, 255, 255),
            "text": (255, 255, 255),
            "text_selected": (255, 230, 92),
            "text_hint": (164, 188, 220),
            "border_dark": (0, 0, 0),
            "border_light": (255, 255, 255),
        }

    def spacing(self, units: float) -> int:
        return int(self.unit * units)
