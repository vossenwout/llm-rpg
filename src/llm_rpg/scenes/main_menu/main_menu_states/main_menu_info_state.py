from __future__ import annotations

import pygame
from llm_rpg.scenes.main_menu.main_menu_states.main_menu_states import MainMenuStates
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import draw_text_panel

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
        margin = self.scene.game.theme.spacing(2)

        title_text = self.scene.game.theme.fonts["large"].render(
            "Game Info", True, self.scene.game.theme.colors["primary"]
        )
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, margin * 4))
        screen.blit(title_text, title_rect)

        info_lines = [
            "Create a character and fight against increasingly difficult enemies.",
            "You can freely type your actions and an LLM will judge the consequences.",
            "Damage is based on AI estimates of feasibility and potential damage and your character's attributes:",
            "  - Attack: influences damage dealt to enemies",
            "  - Defense: influences damage taken from enemies",
            "  - HP: how much damage you can take",
            "  - Focus: How many characters you can type in each turn",
        ]

        panel_width = screen.get_width() - margin * 10

        draw_text_panel(
            screen,
            info_lines,
            self.scene.game.theme.fonts["small"],
            self.scene.game.theme,
            text_color=self.scene.game.theme.colors["text"],
            align="left",
            max_width=panel_width,
            auto_wrap=True,
        )

        back_text = self.scene.game.theme.fonts["small"].render(
            "Press ENTER or ESC to go back",
            True,
            self.scene.game.theme.colors["text_selected"],
        )
        back_rect = back_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - margin)
        )
        screen.blit(back_text, back_rect)
