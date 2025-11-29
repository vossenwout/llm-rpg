from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.resting_hub.resting_hub_states.resting_hub_states import (
    RestingHubStates,
)
from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State

if TYPE_CHECKING:
    from llm_rpg.scenes.resting_hub.resting_hub_scene import RestingHubScene


class RestingHubNavigationState(State):
    def __init__(self, resting_hub_scene: RestingHubScene):
        self.resting_hub_scene = resting_hub_scene
        self.menu_options = {1: "View Character", 2: "Next Battle"}
        self.selected_index = 1
        self.option_selected = False
        self.error_message = ""

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
                self.resting_hub_scene.change_state(RestingHubStates.VIEW_CHARACTER)
            elif self.selected_index == 2:
                self.resting_hub_scene.game.change_scene(SceneTypes.BATTLE)

    def render(self, screen: pygame.Surface):
        screen.fill(self.resting_hub_scene.game.theme.colors["background"])

        title = self.resting_hub_scene.game.theme.fonts["title"].render(
            "Resting Hub", True, self.resting_hub_scene.game.theme.colors["primary"]
        )
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 80)))

        subtitle = self.resting_hub_scene.game.theme.fonts["small"].render(
            f"Battles won: {self.resting_hub_scene.game.battles_won}",
            True,
            self.resting_hub_scene.game.theme.colors["text_hint"],
        )
        screen.blit(subtitle, (40, 140))

        start_y = 220
        spacing = 70
        for index, option in self.menu_options.items():
            is_selected = index == self.selected_index
            color = (
                self.resting_hub_scene.game.theme.colors["text_selected"]
                if is_selected
                else self.resting_hub_scene.game.theme.colors["text"]
            )
            prefix = "> " if is_selected else "  "
            text_surface = self.resting_hub_scene.game.theme.fonts["large"].render(
                prefix + option, True, color
            )
            text_rect = text_surface.get_rect(
                center=(screen.get_width() // 2, start_y + (index - 1) * spacing)
            )
            screen.blit(text_surface, text_rect)

        hint = self.resting_hub_scene.game.theme.fonts["small"].render(
            "Use ↑/↓ and Enter",
            True,
            self.resting_hub_scene.game.theme.colors["text_hint"],
        )
        screen.blit(
            hint,
            hint.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50)),
        )
