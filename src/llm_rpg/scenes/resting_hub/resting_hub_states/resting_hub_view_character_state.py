from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.resting_hub.resting_hub_states.resting_hub_states import (
    RestingHubStates,
)
from llm_rpg.scenes.state import State

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
        screen.fill(self.resting_hub_scene.game.theme.colors["background"])
        hero = self.resting_hub_scene.game.hero

        title = self.resting_hub_scene.game.theme.fonts["title"].render(
            "Character", True, self.resting_hub_scene.game.theme.colors["primary"]
        )
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 60)))

        # Basic info
        info_lines = [
            f"Name: {hero.name}",
            f"Level: {hero.level}",
            f"Class: {hero.class_name}",
            f"Description: {hero.description}",
        ]
        y = 140
        for line in info_lines:
            surf = self.resting_hub_scene.game.theme.fonts["medium"].render(
                line, True, self.resting_hub_scene.game.theme.colors["text"]
            )
            screen.blit(surf, (40, y))
            y += 36

        # Stats
        stats = hero.get_current_stats()
        stat_lines = [
            f"Attack: {stats.attack}",
            f"Defense: {stats.defense}",
            f"Focus: {stats.focus}",
            f"HP: {stats.max_hp}",
        ]
        y += 12
        for line in stat_lines:
            surf = self.resting_hub_scene.game.theme.fonts["small"].render(
                line, True, self.resting_hub_scene.game.theme.colors["text"]
            )
            screen.blit(surf, (40, y))
            y += 22

        # Items
        items_title = self.resting_hub_scene.game.theme.fonts["medium"].render(
            "Items:", True, self.resting_hub_scene.game.theme.colors["text_selected"]
        )
        screen.blit(items_title, (40, y + 10))
        y += 40

        if hero.inventory.items:
            for item in hero.inventory.items:
                line = f"- {item.name} ({item.rarity.value}): {item.description}"
                surf = self.resting_hub_scene.game.theme.fonts["small"].render(
                    line, True, self.resting_hub_scene.game.theme.colors["text"]
                )
                screen.blit(surf, (50, y))
                y += 22
        else:
            surf = self.resting_hub_scene.game.theme.fonts["small"].render(
                "No items equipped.",
                True,
                self.resting_hub_scene.game.theme.colors["text_hint"],
            )
            screen.blit(surf, (50, y))
            y += 22

        hint = self.resting_hub_scene.game.theme.fonts["small"].render(
            "Press Enter/Esc to go back",
            True,
            self.resting_hub_scene.game.theme.colors["text_hint"],
        )
        screen.blit(
            hint,
            hint.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40)),
        )
