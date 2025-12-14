from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import draw_selection_panel, draw_text_panel

if TYPE_CHECKING:
    from llm_rpg.scenes.hero_creation.hero_creation_scene import HeroCreationScene
    from llm_rpg.systems.hero.hero import HeroClass


class HeroCreationChooseClassState(State):
    def __init__(self, scene: HeroCreationScene):
        self.scene = scene
        self.hero_classes: list[HeroClass] = [
            scene.game.config.attack_hero_class,
            scene.game.config.defense_hero_class,
            scene.game.config.focus_hero_class,
        ]
        self.class_info_lines: dict[str, list[str]] = {
            hero_class.class_name: self._build_info_lines(hero_class)
            for hero_class in self.hero_classes
        }
        self.selected_index = 0
        self.confirm_selected = False

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index += 1
                if self.selected_index >= len(self.hero_classes):
                    self.selected_index = 0
            elif event.key == pygame.K_UP:
                self.selected_index -= 1
                if self.selected_index < 0:
                    self.selected_index = len(self.hero_classes) - 1
            elif event.key == pygame.K_RETURN:
                self.confirm_selected = True

    def update(self, dt: float):
        if self.confirm_selected:
            chosen_class = self.hero_classes[self.selected_index]
            self.scene.game.hero.base_stats = chosen_class.base_stats
            self.scene.game.hero.description = chosen_class.description
            self.scene.game.hero.class_name = chosen_class.class_name
            self.scene.game.hero.inventory.add_item(chosen_class.starting_item)
            self.scene.game.hero.full_heal()
            self.scene.game.change_scene(SceneTypes.RESTING_HUB)

    def render(self, screen: pygame.Surface):
        theme = self.scene.game.theme
        spacing = theme.spacing
        screen.fill(theme.colors["background"])

        title_text = theme.fonts["medium"].render(
            "Choose Your Class", True, theme.colors["primary"]
        )
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, spacing(8)))
        screen.blit(title_text, title_rect)

        options = [hero_class.class_name for hero_class in self.hero_classes]

        margin = spacing(2)
        available_width = screen.get_width() - margin * 2
        selector_width = int(available_width * 0.35)
        info_width = available_width - selector_width - spacing(2)

        draw_selection_panel(
            screen=screen,
            options=options,
            selected_index=self.selected_index,
            font=theme.fonts["small"],
            theme=theme,
            x=margin,
            width=selector_width,
            align="left",
        )

        selected_class = self.hero_classes[self.selected_index]
        info_lines = self.class_info_lines[selected_class.class_name]
        draw_text_panel(
            screen=screen,
            lines=info_lines,
            font=theme.fonts["small"],
            theme=theme,
            x=margin + selector_width + spacing(2),
            width=info_width,
            max_width=info_width,
            align="left",
            auto_wrap=True,
        )

        instruction_surface = theme.fonts["small"].render(
            "Press ENTER to confirm",
            True,
            theme.colors["text_hint"],
        )
        instruction_rect = instruction_surface.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - spacing(2))
        )
        screen.blit(instruction_surface, instruction_rect)

    def _build_info_lines(self, hero_class: HeroClass) -> list[str]:
        starting_item = hero_class.starting_item
        return [
            f"Description: {hero_class.description}",
            "",
            f"Starting Item: {starting_item.name}",
            f"{starting_item.description}",
        ]
