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

        title_text = self.scene.game.theme.fonts["medium"].render(
            "Game Over", False, self.scene.game.theme.colors["primary"]
        )
        screen.blit(
            title_text,
            title_text.get_rect(center=(screen.get_width() // 2, spacing(2))),
        )

        # Placeholder graphic block
        placeholder_surface = self.scene.game.theme.fonts["large"].render(
            "☠", False, self.scene.game.theme.colors["text"]
        )
        screen.blit(
            placeholder_surface,
            placeholder_surface.get_rect(
                center=(screen.get_width() // 2, spacing(3.5))
            ),
        )

        draw_selection_panel(
            screen=screen,
            options=list(self.menu_options.values()),
            selected_index=self.selected_index - 1,
            font=self.scene.game.theme.fonts["medium"],
            theme=self.scene.game.theme,
            y=spacing(5),
            width=screen.get_width() - spacing(4),
            padding=spacing(1.5),
            option_spacing=spacing(2),
        )
