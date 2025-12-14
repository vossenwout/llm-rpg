from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import draw_selection_panel

if TYPE_CHECKING:
    from llm_rpg.scenes.game_over.game_over_scene import GameOverScene


class GameOverEndScreenState(State):
    def __init__(self, scene: GameOverScene):
        self.scene = scene
        self.menu_options = {1: "Main Menu", 2: "Quit"}
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
                self.scene.game.change_scene(SceneTypes.MAIN_MENU)
            elif self.selected_index == 2:
                self.scene.game.is_running = False

    def render(self, screen: pygame.Surface):
        screen.fill(self.scene.game.theme.colors["background"])
        spacing = self.scene.game.theme.spacing

        title_surface = self.scene.game.theme.fonts["medium"].render(
            "Game Over", False, self.scene.game.theme.colors["primary"]
        )
        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, spacing(4))
        )
        screen.blit(title_surface, title_rect)

        margin = spacing(2)
        panel_width = screen.get_width() - margin * 6
        panel_y = title_rect.bottom + margin

        draw_selection_panel(
            screen=screen,
            options=list(self.menu_options.values()),
            selected_index=self.selected_index - 1,
            font=self.scene.game.theme.fonts["small"],
            theme=self.scene.game.theme,
            y=panel_y,
            width=panel_width,
            padding=spacing(2),
            option_spacing=spacing(1),
            align="center",
        )
