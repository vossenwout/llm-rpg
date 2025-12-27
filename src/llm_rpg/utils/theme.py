import pygame

from llm_rpg.utils.assets import asset_file


class Theme:
    def __init__(self) -> None:
        self.unit = 4
        with asset_file("fonts/earthbound.ttf") as earthbound_path:
            self.fonts = {
                "large": pygame.font.Font(earthbound_path, 64),
                "medium": pygame.font.Font(earthbound_path, 32),
                "small": pygame.font.Font(earthbound_path, 16),
            }
        with asset_file("sprites/panel_border.png") as panel_border_path:
            base_panel_border = pygame.image.load(panel_border_path)
            self.panel_border = base_panel_border
        with asset_file("sprites/checkboard.png") as checkerboard_path:
            self.checkerboard_background = pygame.image.load(checkerboard_path)

        self.colors = {
            "background": (0, 0, 0),
            "panel": (255, 255, 255),
            "panel_inner": (0, 0, 0),
            "primary": (255, 255, 255),
            "text": (255, 255, 255),
            "text_selected": (255, 230, 92),
            "text_hint": (164, 188, 220),
            "text_hint_shadow": (0, 0, 0, 200),
            "hud_backdrop": (8, 10, 12, 140),
            "hud_border": (255, 255, 255, 120),
            "text_items": (120, 255, 180),
            "border_dark": (0, 0, 0),
            "border_light": (255, 255, 255),
        }

    def spacing(self, units: float) -> int:
        return int(self.unit * units)
