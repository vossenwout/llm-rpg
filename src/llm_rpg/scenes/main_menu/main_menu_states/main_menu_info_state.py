from __future__ import annotations

import pygame
from llm_rpg.scenes.main_menu.main_menu_states.main_menu_states import MainMenuStates
from llm_rpg.scenes.state import State
from llm_rpg.utils.ui import draw_panel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_rpg.scenes.main_menu.main_menu_scene import MainMenuScene


class MainMenuInfoState(State):
    def __init__(self, scene: MainMenuScene):
        self.scene = scene
        self.back_selected = False

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.back_selected = True

    def update(self, dt: float):
        if self.back_selected:
            self.scene.change_state(MainMenuStates.NAVIGATION)

    def render(self, screen: pygame.Surface):
        screen.fill(self.scene.game.theme.colors["background"])

        title_text = self.scene.game.theme.fonts["title"].render(
            "Game Info", True, self.scene.game.theme.colors["primary"]
        )
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 80))
        screen.blit(title_text, title_rect)

        panel_rect = pygame.Rect(80, 140, screen.get_width() - 160, 360)
        draw_panel(screen, panel_rect, self.scene.game.theme)

        info_lines = [
            "You choose a character class and fight against increasingly difficult enemies.",
            "You can freely type your actions and an LLM will judge the consequences.",
            "LLM will judge your action based on the battle situation, your character class, and your items.",
            "LLM will output: feasibility of action and potential damage.",
            "",
            "Besides LLM-based damage, your character has the following attributes:",
            "  - Attack: influences damage dealt to enemies",
            "  - Defense: influences damage taken from enemies",
            "  - HP: how much damage you can take",
            "  - Focus: How many characters you can type in each turn",
        ]

        start_y = 180
        line_spacing = 35
        for i, line in enumerate(info_lines):
            text_surface = self.scene.game.theme.fonts["small"].render(
                line, True, self.scene.game.theme.colors["text"]
            )
            text_rect = text_surface.get_rect(
                center=(screen.get_width() // 2, start_y + i * line_spacing)
            )
            screen.blit(text_surface, text_rect)

        back_text = self.scene.game.theme.fonts["medium"].render(
            "Press ENTER or ESC to go back",
            True,
            self.scene.game.theme.colors["text_selected"],
        )
        back_rect = back_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - 60)
        )
        screen.blit(back_text, back_rect)
