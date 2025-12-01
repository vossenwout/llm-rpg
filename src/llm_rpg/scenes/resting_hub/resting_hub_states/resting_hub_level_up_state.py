from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.objects.character import StatTypes
from llm_rpg.scenes.resting_hub.resting_hub_states.resting_hub_states import (
    RestingHubStates,
)
from llm_rpg.scenes.state import State

if TYPE_CHECKING:
    from llm_rpg.scenes.resting_hub.resting_hub_scene import RestingHubScene


class RestingHubLevelUpState(State):
    def __init__(self, resting_hub_scene: RestingHubScene):
        self.resting_hub_scene = resting_hub_scene
        self.stat_options = {
            1: StatTypes.ATTACK,
            2: StatTypes.DEFENSE,
            3: StatTypes.FOCUS,
            4: StatTypes.MAX_HP,
        }
        self.selected_index = 1
        self.option_selected = False
        self.stat_increase_per_level = 5

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index += 1
                if self.selected_index > len(self.stat_options):
                    self.selected_index = 1
            elif event.key == pygame.K_UP:
                self.selected_index -= 1
                if self.selected_index < 1:
                    self.selected_index = len(self.stat_options)
            elif event.key == pygame.K_RETURN:
                self.option_selected = True

    def update(self, dt: float):
        hero = self.resting_hub_scene.game.hero
        if not hero.should_level_up:
            self.resting_hub_scene.change_state(RestingHubStates.NAVIGATION)
            return

        if self.option_selected:
            self.option_selected = False
            stat_type = self.stat_options[self.selected_index]
            hero.level_up(stat_type, self.stat_increase_per_level)
            self.feedback_message = (
                f"{stat_type.value} increased by {self.stat_increase_per_level}!"
            )
            # After level up, move back to navigation
            self.resting_hub_scene.change_state(RestingHubStates.NAVIGATION)

    def render(self, screen: pygame.Surface):
        screen.fill(self.resting_hub_scene.game.theme.colors["background"])
        spacing = self.resting_hub_scene.game.theme.spacing

        title = self.resting_hub_scene.game.theme.fonts["title"].render(
            "Level Up!", True, self.resting_hub_scene.game.theme.colors["primary"]
        )
        screen.blit(
            title, title.get_rect(center=(screen.get_width() // 2, spacing(1.5)))
        )

        prompt = self.resting_hub_scene.game.theme.fonts["medium"].render(
            "Choose a stat to increase",
            True,
            self.resting_hub_scene.game.theme.colors["text"],
        )
        screen.blit(
            prompt, prompt.get_rect(center=(screen.get_width() // 2, spacing(2.75)))
        )

        start_y = spacing(3.5)
        vertical_step = spacing(2)
        for index, stat in self.stat_options.items():
            is_selected = index == self.selected_index
            color = (
                self.resting_hub_scene.game.theme.colors["text_selected"]
                if is_selected
                else self.resting_hub_scene.game.theme.colors["text"]
            )
            prefix = "> " if is_selected else "  "
            label = (
                f"{prefix}{stat.value.capitalize()} (+{self.stat_increase_per_level})"
            )
            surf = self.resting_hub_scene.game.theme.fonts["large"].render(
                label, True, color
            )
            screen.blit(
                surf,
                surf.get_rect(
                    center=(
                        screen.get_width() // 2,
                        start_y + (index - 1) * vertical_step,
                    )
                ),
            )

        hint = self.resting_hub_scene.game.theme.fonts["small"].render(
            "Use ↑/↓ and Enter",
            True,
            self.resting_hub_scene.game.theme.colors["text_hint"],
        )
        screen.blit(
            hint,
            hint.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - spacing(1))
            ),
        )
