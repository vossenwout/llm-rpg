from __future__ import annotations

import random
import pygame
from typing import TYPE_CHECKING, List, Optional

from llm_rpg.objects.item import (
    ALL_ITEMS,
    Item,
)
from llm_rpg.scenes.resting_hub.resting_hub_states.resting_hub_states import (
    RestingHubStates,
)
from llm_rpg.scenes.state import State

if TYPE_CHECKING:
    from llm_rpg.scenes.resting_hub.resting_hub_scene import RestingHubScene


class RestingHubGetItemState(State):
    def __init__(self, resting_hub_scene: RestingHubScene):
        self.resting_hub_scene = resting_hub_scene
        self.message_queue: list[str] = []
        self.selected_item: Optional[Item] = None
        self.is_replacing_item = False
        self.n_items_to_drop = 3
        self.items: List[Item] = self._initialize_items()
        self.selected_index = 0  # includes cancel at index 0
        self.chosen_item: Optional[Item] = None
        self.choice_made = False

    def _initialize_items(self):
        all_possible_items = ALL_ITEMS
        items_to_choose_from = []
        for item in all_possible_items:
            is_not_equiped = True
            for equipped_item in self.resting_hub_scene.game.hero.inventory.items:
                if equipped_item.name == item.name:
                    is_not_equiped = False
                    break
            if is_not_equiped:
                items_to_choose_from.append(item)
        n_items_to_drop = min(self.n_items_to_drop, len(items_to_choose_from))
        return random.sample(items_to_choose_from, n_items_to_drop)

    def _current_options(self) -> list[str]:
        if self.is_replacing_item:
            options = ["Cancel"]
            for item in self.resting_hub_scene.game.hero.inventory.items:
                options.append(f"Replace {item.name}: {item.description}")
            return options
        else:
            options = ["Don't pick up anything"]
            for item in self.items:
                options.append(f"{item.name}: {item.description}")
            return options

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            options_len = len(self._current_options())
            if event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % options_len
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % options_len
            elif event.key == pygame.K_RETURN:
                self.choice_made = True

    def update(self, dt: float):
        hero = self.resting_hub_scene.game.hero
        if not hero.discovered_item:
            self.resting_hub_scene.change_state(RestingHubStates.NAVIGATION)
            return

        if not self.choice_made:
            return

        self.choice_made = False
        if self.is_replacing_item:
            if self.selected_index == 0:
                # cancel replacing, show discovered items again
                self.is_replacing_item = False
                self.selected_index = 0
                return
            item_to_remove = hero.inventory.items[self.selected_index - 1]
            hero.replace_item_with_discovered_item(
                item_to_remove=item_to_remove, discovered_item=self.chosen_item
            )
            self.message_queue.append(
                f"Replaced {item_to_remove.name} with {self.chosen_item.name}."
            )
            hero.discovered_item = False
        else:
            if self.selected_index == 0:
                hero.dont_pick_up_item()
                hero.discovered_item = False
            else:
                self.chosen_item = self.items[self.selected_index - 1]
                if hero.inventory.is_full():
                    self.is_replacing_item = True
                    self.selected_index = 0
                    return
                hero.pick_up_discovered_item(self.chosen_item)
                self.message_queue.append(f"Picked up {self.chosen_item.name}.")
                hero.discovered_item = False

    def _render_messages(self, screen: pygame.Surface, start_y: int):
        for i, message in enumerate(self.message_queue[-3:]):
            surf = self.resting_hub_scene.game.theme.fonts["small"].render(
                message, True, self.resting_hub_scene.game.theme.colors["text_selected"]
            )
            screen.blit(surf, (60, start_y + i * 22))

    def render(self, screen: pygame.Surface):
        screen.fill(self.resting_hub_scene.game.theme.colors["background"])
        spacing = self.resting_hub_scene.game.theme.spacing

        title = self.resting_hub_scene.game.theme.fonts["title"].render(
            "Item Discovery", True, self.resting_hub_scene.game.theme.colors["primary"]
        )
        screen.blit(
            title, title.get_rect(center=(screen.get_width() // 2, spacing(1.25)))
        )

        subtitle = self.resting_hub_scene.game.theme.fonts["small"].render(
            "Select an item to pick up (or skip)",
            True,
            self.resting_hub_scene.game.theme.colors["text_hint"],
        )
        screen.blit(
            subtitle, subtitle.get_rect(center=(screen.get_width() // 2, spacing(2.25)))
        )

        options = self._current_options()
        start_y = spacing(3)
        vertical_step = spacing(2)
        for idx, text in enumerate(options):
            is_selected = idx == self.selected_index
            color = (
                self.resting_hub_scene.game.theme.colors["text_selected"]
                if is_selected
                else self.resting_hub_scene.game.theme.colors["text"]
            )
            prefix = "> " if is_selected else "  "
            surf = self.resting_hub_scene.game.theme.fonts["medium"].render(
                prefix + text, True, color
            )
            screen.blit(surf, (spacing(0.5), start_y + idx * vertical_step))

        self._render_messages(
            screen, start_y + len(options) * vertical_step + spacing(0.25)
        )

        hint = self.resting_hub_scene.game.theme.fonts["small"].render(
            "Use ↑/↓ and Enter",
            True,
            self.resting_hub_scene.game.theme.colors["text_hint"],
        )
        screen.blit(
            hint,
            hint.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - spacing(0.5))
            ),
        )
