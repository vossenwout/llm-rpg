from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.objects.character import StatTypes
from llm_rpg.scenes.resting_hub.resting_hub_states.resting_hub_states import (
    RestingHubStates,
)
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import draw_selection_panel, draw_text_panel

if TYPE_CHECKING:
    from llm_rpg.scenes.resting_hub.resting_hub_scene import RestingHubScene


class RestingHubLevelUpState(State):
    def __init__(self, resting_hub_scene: RestingHubScene):
        self.resting_hub_scene = resting_hub_scene
        self.stat_options: list[StatTypes] = [
            StatTypes.ATTACK,
            StatTypes.DEFENSE,
            StatTypes.FOCUS,
            StatTypes.MAX_HP,
        ]
        self.selected_index = 0
        self.option_selected = False
        self.stat_increase_per_level = 5

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index += 1
                if self.selected_index >= len(self.stat_options):
                    self.selected_index = 0
            elif event.key == pygame.K_UP:
                self.selected_index -= 1
                if self.selected_index < 0:
                    self.selected_index = len(self.stat_options) - 1
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
            self.resting_hub_scene.change_state(RestingHubStates.NAVIGATION)

    def render(self, screen: pygame.Surface):
        theme = self.resting_hub_scene.game.theme
        spacing = theme.spacing
        screen.fill(theme.colors["background"])

        title_surface = theme.fonts["large"].render(
            "Level Up!", True, theme.colors["primary"]
        )
        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, spacing(2))
        )
        screen.blit(title_surface, title_rect)

        margin = spacing(2)
        panel_width = screen.get_width() - margin * 4

        prompt_rect = draw_text_panel(
            screen=screen,
            lines=f"Choose a stat to increase (+{self.stat_increase_per_level})",
            font=theme.fonts["small"],
            theme=theme,
            x=margin,
            y=title_rect.bottom + spacing(1),
            width=panel_width,
            align="left",
            auto_wrap=True,
            draw_border=False,
        )

        stat_labels = [
            f"{stat.value.capitalize()} (+{self.stat_increase_per_level})"
            for stat in self.stat_options
        ]

        draw_selection_panel(
            screen=screen,
            options=stat_labels,
            selected_index=self.selected_index,
            font=theme.fonts["medium"],
            theme=theme,
            x=margin,
            y=prompt_rect.bottom + spacing(1.5),
            width=panel_width,
            padding=spacing(2),
            option_spacing=spacing(1.5),
            align="left",
        )

        hint = theme.fonts["small"].render(
            "Use arrows to navigate, Enter to confirm",
            True,
            theme.colors["text_hint"],
        )
        screen.blit(
            hint,
            hint.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - spacing(1))
            ),
        )
