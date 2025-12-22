from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State
from llm_rpg.scenes.main_menu.main_menu_states.main_menu_states import MainMenuStates
from llm_rpg.ui.components import draw_selection_panel
from llm_rpg.utils.assets import asset_file

if TYPE_CHECKING:
    from llm_rpg.scenes.main_menu.main_menu_scene import MainMenuScene


class MainMenuNavigationState(State):
    def __init__(self, scene: MainMenuScene) -> None:
        self.scene = scene
        self.menu_options = {
            1: "Start New Game",
            2: "Info",
        }
        self.selected_index = 1
        self.option_selected = False
        with asset_file("sprites/logo.png") as logo_path:
            self.logo_surface = pygame.image.load(logo_path).convert_alpha()
        self.logo_scaled_surface = self._scale_logo()

    def handle_input(self, event: pygame.event.Event) -> None:
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

    def update(self, dt: float) -> None:
        if self.option_selected:
            if self.selected_index == 1:
                self.scene.game.change_scene(SceneTypes.HERO_CREATION)
            elif self.selected_index == 2:
                self.scene.change_state(MainMenuStates.INFO)

    def _scale_logo(self) -> pygame.Surface:
        margin = self.scene.game.theme.spacing(2)
        max_width = self.scene.game.DESIGN_WIDTH - margin * 8
        max_height = self.scene.game.DESIGN_HEIGHT // 4

        logo_width = self.logo_surface.get_width()
        logo_height = self.logo_surface.get_height()

        target_width = min(logo_width, max_width)
        target_height = min(logo_height, max_height)
        scale = min(target_width / logo_width, target_height / logo_height, 1.0)
        scaled_size = (
            max(1, int(logo_width * scale)),
            max(1, int(logo_height * scale)),
        )

        if scale < 1.0:
            return pygame.transform.scale(self.logo_surface, scaled_size)

        return self.logo_surface

    def _render_logo(self, screen: pygame.Surface) -> pygame.Rect:
        logo_surface = self.logo_scaled_surface
        logo_rect = logo_surface.get_rect(
            center=(screen.get_width() // 2, int(screen.get_height() * 0.3))
        )
        screen.blit(logo_surface, logo_rect)
        return logo_rect

    def _render_menu_options(
        self, screen: pygame.Surface, y: int | None = None
    ) -> pygame.Rect:
        margin = self.scene.game.theme.spacing(2)
        panel_width = screen.get_width() - margin * 6
        return draw_selection_panel(
            screen=screen,
            options=list(self.menu_options.values()),
            selected_index=self.selected_index - 1,
            font=self.scene.game.theme.fonts["small"],
            theme=self.scene.game.theme,
            padding=self.scene.game.theme.spacing(2),
            option_spacing=self.scene.game.theme.spacing(1),
            width=panel_width,
            align="center",
            y=y,
        )

    def render(self, screen: pygame.Surface) -> None:
        screen.fill(self.scene.game.theme.colors["background"])
        logo_rect = self._render_logo(screen=screen)
        menu_y = logo_rect.bottom + self.scene.game.theme.spacing(8)
        self._render_menu_options(screen=screen, y=menu_y)
