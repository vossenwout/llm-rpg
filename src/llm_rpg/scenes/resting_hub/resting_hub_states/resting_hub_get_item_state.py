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
from llm_rpg.ui.components import draw_selection_panel, draw_text_panel

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

    def _initialize_items(self) -> List[Item]:
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

    def render(self, screen: pygame.Surface):
        theme = self.resting_hub_scene.game.theme
        spacing = theme.spacing
        screen.fill(theme.colors["background"])

        title_surface = theme.fonts["medium"].render(
            "Item Discovery", True, theme.colors["primary"]
        )
        title_rect = title_surface.get_rect(
            center=(screen.get_width() // 2, spacing(6))
        )
        screen.blit(title_surface, title_rect)

        margin = spacing(2)
        panel_width = screen.get_width() - margin * 4

        subtitle_rect = draw_text_panel(
            screen=screen,
            lines="Select an item to pick up (or skip)",
            font=theme.fonts["small"],
            theme=theme,
            x=margin,
            y=title_rect.bottom + spacing(1),
            width=panel_width,
            align="left",
            auto_wrap=True,
            draw_border=False,
        )

        options = self._current_options()
        options_rect = draw_selection_panel(
            screen=screen,
            options=options,
            selected_index=self.selected_index,
            font=theme.fonts["small"],
            theme=theme,
            x=margin,
            y=subtitle_rect.bottom + spacing(1.5),
            width=panel_width,
            padding=spacing(2),
            option_spacing=spacing(1.5),
            align="left",
        )

        if self.message_queue:
            draw_text_panel(
                screen=screen,
                lines=self.message_queue[-3:],
                font=theme.fonts["small"],
                theme=theme,
                x=margin,
                y=options_rect.bottom + spacing(1),
                width=panel_width,
                align="left",
                auto_wrap=True,
                draw_border=False,
            )

        hint = theme.fonts["small"].render(
            "Use arrows to navigate, Enter to confirm",
            True,
            theme.colors["text_hint"],
        )
        screen.blit(
            hint,
            hint.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - spacing(2))
            ),
        )
