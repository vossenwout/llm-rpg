from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.resting_hub.resting_hub_states.resting_hub_states import (
    RestingHubStates,
)
from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import draw_selection_panel, draw_text_panel

if TYPE_CHECKING:
    from llm_rpg.scenes.resting_hub.resting_hub_scene import RestingHubScene


class RestingHubNavigationState(State):
    def __init__(self, resting_hub_scene: RestingHubScene):
        self.resting_hub_scene = resting_hub_scene
        self.menu_options: list[str] = ["Next Battle", "View Character"]
        self.selected_index = 0
        self.option_selected = False
        self.error_message = ""

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index += 1
                if self.selected_index >= len(self.menu_options):
                    self.selected_index = 0
            elif event.key == pygame.K_UP:
                self.selected_index -= 1
                if self.selected_index < 0:
                    self.selected_index = len(self.menu_options) - 1
            elif event.key == pygame.K_RETURN:
                self.option_selected = True

    def update(self, dt: float):
        if self.option_selected:
            if self.selected_index == 0:
                self.resting_hub_scene.game.change_scene(SceneTypes.BATTLE)
            elif self.selected_index == 1:
                self.resting_hub_scene.change_state(RestingHubStates.VIEW_CHARACTER)

    def render(self, screen: pygame.Surface):
        theme = self.resting_hub_scene.game.theme
        spacing = theme.spacing
        screen.fill(theme.colors["background"])

        title_surface = theme.fonts["large"].render(
            "Resting Hub", True, theme.colors["primary"]
        )
        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, spacing(8))
        )
        screen.blit(title_surface, title_rect)

        margin = spacing(2)
        panel_width = screen.get_width() - margin * 4

        info_rect = draw_text_panel(
            screen=screen,
            lines=f"Battles won: {self.resting_hub_scene.game.battles_won}",
            font=theme.fonts["small"],
            theme=theme,
            x=margin,
            y=title_rect.bottom + spacing(2),
            width=panel_width,
            align="left",
            auto_wrap=False,
            draw_border=False,
        )

        draw_selection_panel(
            screen=screen,
            options=self.menu_options,
            selected_index=self.selected_index,
            font=theme.fonts["small"],
            theme=theme,
            x=margin,
            y=info_rect.bottom + spacing(1.5),
            width=panel_width,
            padding=spacing(2),
            option_spacing=spacing(1.5),
            align="left",
        )

        hint = theme.fonts["small"].render(
            "Use ↑/↓ and Enter",
            True,
            theme.colors["text_hint"],
        )
        screen.blit(
            hint,
            hint.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - spacing(1))
            ),
        )
