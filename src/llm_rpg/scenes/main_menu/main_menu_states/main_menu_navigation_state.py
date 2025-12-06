from __future__ import annotations

import pygame
from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State
from typing import TYPE_CHECKING
from llm_rpg.scenes.main_menu.main_menu_states.main_menu_states import MainMenuStates
from llm_rpg.ui.components import draw_selection_panel

if TYPE_CHECKING:
    from llm_rpg.scenes.main_menu.main_menu_scene import MainMenuScene


class MainMenuNavigationState(State):
    def __init__(self, scene: MainMenuScene):
        self.scene = scene
        self.menu_options = {
            1: "Start New Game",
            2: "Info",
        }
        self.selected_index = 1
        self.option_selected = False

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index += 1
                if self.selected_index > len(self.menu_options):
                    self.selected_index = 1
            elif event.key == pygame.K_UP:
                self.selected_index -= 1
                if self.selected_index < 1:
                    self.selected_index = len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                self.option_selected = True

    def update(self, dt: float):
        if self.option_selected:
            if self.selected_index == 1:
                self.scene.game.change_scene(SceneTypes.HERO_CREATION)
            elif self.selected_index == 2:
                self.scene.change_state(MainMenuStates.INFO)

    def _render_logo(self, screen: pygame.Surface):
        margin = self.scene.game.theme.spacing(2)
        logo_surface = self.scene.game.theme.fonts["title"].render(
            "LLM RPG", False, self.scene.game.theme.colors["primary"]
        )
        logo_rect = logo_surface.get_rect(center=(screen.get_width() // 2, margin * 6))
        screen.blit(logo_surface, logo_rect)

    def _render_menu_options(self, screen: pygame.Surface):
        margin = self.scene.game.theme.spacing(2)
        panel_width = screen.get_width() - margin * 6
        draw_selection_panel(
            screen=screen,
            options=list(self.menu_options.values()),
            selected_index=self.selected_index - 1,
            font=self.scene.game.theme.fonts["medium"],
            theme=self.scene.game.theme,
            padding=self.scene.game.theme.spacing(2),
            option_spacing=self.scene.game.theme.spacing(1),
            panel_width=panel_width,
            align="center",
        )

    def render(self, screen: pygame.Surface):
        screen.fill(self.scene.game.theme.colors["background"])
        self._render_logo(screen=screen)
        self._render_menu_options(screen=screen)
