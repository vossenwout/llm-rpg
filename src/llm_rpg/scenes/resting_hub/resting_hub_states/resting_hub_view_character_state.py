from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.resting_hub.resting_hub_states.resting_hub_states import (
    RestingHubStates,
)
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import draw_text_panel

if TYPE_CHECKING:
    from llm_rpg.scenes.resting_hub.resting_hub_scene import RestingHubScene


class RestingHubViewCharacterState(State):
    def __init__(self, resting_hub_scene: RestingHubScene):
        self.resting_hub_scene = resting_hub_scene

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN,
            pygame.K_ESCAPE,
            pygame.K_BACKSPACE,
        ):
            self.resting_hub_scene.change_state(RestingHubStates.NAVIGATION)

    def update(self, dt: float):
        pass

    def render(self, screen: pygame.Surface):
        theme = self.resting_hub_scene.game.theme
        spacing = theme.spacing
        hero = self.resting_hub_scene.game.hero
        screen.fill(theme.colors["background"])

        title_surface = theme.fonts["large"].render(
            "Character", True, theme.colors["primary"]
        )
        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, spacing(2))
        )
        screen.blit(title_surface, title_rect)

        margin = spacing(2)
        panel_width = screen.get_width() - margin * 4

        stats = hero.get_current_stats()
        item_lines = [
            f"- {item.name} ({item.rarity.value}): {item.description}"
            for item in hero.inventory.items
        ] or ["No items equipped."]

        info_lines = [
            f"Name: {hero.name}",
            f"Level: {hero.level}",
            f"Class: {hero.class_name}",
            f"Description: {hero.description}",
            "",
            "Stats:",
            f"Attack: {stats.attack}",
            f"Defense: {stats.defense}",
            f"Focus: {stats.focus}",
            f"HP: {stats.max_hp}",
            "",
            "Items:",
            *item_lines,
        ]

        draw_text_panel(
            screen=screen,
            lines=info_lines,
            font=theme.fonts["small"],
            theme=theme,
            x=margin,
            y=title_rect.bottom + spacing(1.5),
            width=panel_width,
            align="left",
            auto_wrap=True,
        )

        hint = theme.fonts["small"].render(
            "Press Enter/Esc to go back",
            True,
            theme.colors["text_hint"],
        )
        screen.blit(
            hint,
            hint.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - spacing(1))
            ),
        )
