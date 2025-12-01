import pygame

from llm_rpg.utils.assets import asset_file


class Theme:
    def __init__(self):
        self.unit = 8
        self.scale = 3
        with asset_file("fonts/PressStart2P-Regular.ttf") as font_path:
            self.fonts = {
                "title": pygame.font.Font(font_path, 48),
                "large": pygame.font.Font(font_path, 32),
                "medium": pygame.font.Font(font_path, 24),
                "small": pygame.font.Font(font_path, 16),
            }

        self.colors = {
            "background": (0, 0, 0),
            "panel": (5, 5, 5),
            "primary": (77, 210, 255),
            "text": (232, 244, 255),
            "text_selected": (255, 238, 128),
            "text_hint": (160, 192, 208),
            "border_dark": (210, 210, 210),
            "border_light": (255, 255, 255),
        }
