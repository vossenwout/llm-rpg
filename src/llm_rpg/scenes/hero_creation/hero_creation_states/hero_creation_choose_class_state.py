from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State

if TYPE_CHECKING:
    from llm_rpg.scenes.hero_creation.hero_creation_scene import HeroCreationScene
    from llm_rpg.systems.hero.hero import HeroClass


class HeroCreationChooseClassState(State):
    def __init__(self, scene: HeroCreationScene):
        self.scene = scene
        self.navigation_class_mapping: dict[int, HeroClass] = {
            1: scene.game.config.attack_hero_class,
            2: scene.game.config.defense_hero_class,
            3: scene.game.config.focus_hero_class,
        }
        self.selected_index = 1
        self.confirm_selected = False

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index += 1
                if self.selected_index > len(self.navigation_class_mapping):
                    self.selected_index = 1
            elif event.key == pygame.K_UP:
                self.selected_index -= 1
                if self.selected_index < 1:
                    self.selected_index = len(self.navigation_class_mapping)
            elif event.key == pygame.K_RETURN:
                self.confirm_selected = True

    def update(self, dt: float):
        if self.confirm_selected:
            chosen_class = self.navigation_class_mapping[self.selected_index]
            self.scene.game.hero.base_stats = chosen_class.base_stats
            self.scene.game.hero.description = chosen_class.description
            self.scene.game.hero.class_name = chosen_class.class_name
            self.scene.game.hero.inventory.add_item(chosen_class.starting_item)
            self.scene.game.hero.full_heal()
            self.scene.game.change_scene(SceneTypes.RESTING_HUB)

    def render(self, screen: pygame.Surface):
        screen.fill(self.scene.game.theme.colors["background"])
        spacing = self.scene.game.theme.spacing

        title_text = self.scene.game.theme.fonts["title"].render(
            "Choose Your Class", True, self.scene.game.theme.colors["primary"]
        )
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, spacing(1.5)))
        screen.blit(title_text, title_rect)

        start_y = spacing(3)
        vertical_step = spacing(2.5)
        for index, hero_class in self.navigation_class_mapping.items():
            is_selected = index == self.selected_index
            color = (
                self.scene.game.theme.colors["text_selected"]
                if is_selected
                else self.scene.game.theme.colors["text"]
            )
            prefix = "> " if is_selected else "  "
            option_text = f"{prefix}{hero_class.class_name}"

            option_surface = self.scene.game.theme.fonts["large"].render(
                option_text, True, color
            )
            option_rect = option_surface.get_rect(
                midleft=(spacing(1), start_y + (index - 1) * vertical_step)
            )
            screen.blit(option_surface, option_rect)

            description_surface = self.scene.game.theme.fonts["small"].render(
                hero_class.description, True, self.scene.game.theme.colors["text"]
            )
            description_rect = description_surface.get_rect(
                topleft=(spacing(1.25), option_rect.bottom + spacing(0.25))
            )
            screen.blit(description_surface, description_rect)

            item_surface = self.scene.game.theme.fonts["small"].render(
                f"Starts with: {hero_class.starting_item.name}",
                True,
                self.scene.game.theme.colors["text_hint"],
            )
            item_rect = item_surface.get_rect(
                topleft=(spacing(1.25), description_rect.bottom + spacing(0.25))
            )
            screen.blit(item_surface, item_rect)

        instruction_surface = self.scene.game.theme.fonts["small"].render(
            "Use ↑/↓ and press Enter to confirm",
            True,
            self.scene.game.theme.colors["text_hint"],
        )
        instruction_rect = instruction_surface.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - spacing(1))
        )
        screen.blit(instruction_surface, instruction_rect)
