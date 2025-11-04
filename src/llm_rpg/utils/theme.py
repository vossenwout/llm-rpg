import pygame


class Theme:
    def __init__(self):
        self.fonts = {
            "title": pygame.font.Font(None, 72),
            "large": pygame.font.Font(None, 48),
            "medium": pygame.font.Font(None, 36),
            "small": pygame.font.Font(None, 24),
        }

        self.colors = {
            "background": (20, 20, 40),
            "primary": (255, 215, 0),  # Gold
            "text": (200, 200, 200),
            "text_selected": (255, 255, 100),
            "text_hint": (150, 150, 150),
        }
