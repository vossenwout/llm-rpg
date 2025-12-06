from __future__ import annotations

import pygame
from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State
from typing import TYPE_CHECKING
from llm_rpg.scenes.main_menu.main_menu_states.main_menu_states import MainMenuStates
from llm_rpg.ui.components import draw_panel

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
        logo_rect = logo_surface.get_rect(center=(screen.get_width() // 2, margin * 2))
        screen.blit(logo_surface, logo_rect)

    def _render_menu_options(self, screen: pygame.Surface):
        margin = self.scene.game.theme.spacing(2)
        panel_width = screen.get_width() - margin * 6
        panel_height = self.scene.game.theme.spacing(11)
        panel_rect = pygame.Rect(
            margin * 3,
            margin * 6,
            panel_width,
            panel_height,
        )
        draw_panel(screen, panel_rect, self.scene.game.theme)
        start_y = panel_rect.top + self.scene.game.theme.spacing(4)
        spacing = self.scene.game.theme.spacing(3)
        for index, option_text in self.menu_options.items():
            is_selected = index == self.selected_index
            color = (
                self.scene.game.theme.colors["text_selected"]
                if is_selected
                else self.scene.game.theme.colors["text"]
            )

            option_surface = self.scene.game.theme.fonts["medium"].render(
                option_text, False, color
            )
            y_pos = start_y + (index - 1) * spacing
            option_rect = option_surface.get_rect(
                center=(screen.get_width() // 2, y_pos)
            )
            screen.blit(option_surface, option_rect)

            if is_selected:
                arrow_size = self.scene.game.theme.spacing(1)
                arrow_x = option_rect.left - self.scene.game.theme.spacing(2)
                arrow_y = option_rect.centery

                points = [
                    (arrow_x, arrow_y),
                    (arrow_x - arrow_size, arrow_y - arrow_size // 2),
                    (arrow_x - arrow_size, arrow_y + arrow_size // 2),
                ]
                pygame.draw.polygon(screen, color, points)

    def render(self, screen: pygame.Surface):
        screen.fill(self.scene.game.theme.colors["background"])
        self._render_logo(screen=screen)
        self._render_menu_options(screen=screen)
