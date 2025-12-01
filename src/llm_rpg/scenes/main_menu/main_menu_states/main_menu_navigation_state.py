from __future__ import annotations

import pygame
from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State
from typing import TYPE_CHECKING
from llm_rpg.scenes.main_menu.main_menu_states.main_menu_states import MainMenuStates
from llm_rpg.utils.ui import draw_panel

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
            if event.key == pygame.K_UP:
                self.selected_index -= 1
                if self.selected_index < 1:
                    self.selected_index = len(self.menu_options)
            if event.key == pygame.K_RETURN:
                self.option_selected = True

    def update(self, dt: float):
        if self.option_selected:
            if self.selected_index == 1:
                self.scene.game.change_scene(SceneTypes.HERO_CREATION)
            elif self.selected_index == 2:
                self.scene.change_state(MainMenuStates.INFO)

    def render(self, screen: pygame.Surface):
        screen.fill(self.scene.game.theme.colors["background"])
        logo_rect = self.scene.logo_sprite.get_rect(
            center=(screen.get_width() // 2, 110)
        )
        screen.blit(self.scene.logo_sprite, logo_rect)

        panel_width = 600
        panel_height = 180
        panel_rect = pygame.Rect(
            (screen.get_width() - panel_width) // 2,
            220,
            panel_width,
            panel_height,
        )
        draw_panel(screen, panel_rect, self.scene.game.theme)

        start_y = panel_rect.top + 40
        spacing = 50
        for index, option_text in self.menu_options.items():
            is_selected = index == self.selected_index
            color = (
                self.scene.game.theme.colors["text_selected"]
                if is_selected
                else self.scene.game.theme.colors["text"]
            )
            prefix = "> " if is_selected else "  "
            full_text = f"{prefix}{option_text}"
            option_surface = self.scene.game.theme.fonts["medium"].render(
                full_text, True, color
            )
            option_rect = option_surface.get_rect(
                center=(screen.get_width() // 2, start_y + (index - 1) * spacing)
            )
            screen.blit(option_surface, option_rect)
