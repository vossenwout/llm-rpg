import pygame

from llm_rpg.utils.assets import asset_file


class Theme:
    def __init__(self):
        self.unit = 4
        with asset_file("fonts/earthbound.ttf") as earthbound_path:
            self.fonts = {
                "large": pygame.font.Font(earthbound_path, 64),
                "medium": pygame.font.Font(earthbound_path, 32),
                "small": pygame.font.Font(earthbound_path, 16),
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
