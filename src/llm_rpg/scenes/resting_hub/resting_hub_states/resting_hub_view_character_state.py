from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.resting_hub.resting_hub_states.resting_hub_states import (
    RestingHubStates,
)
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import (
    draw_text_panel,
    measure_text_block,
    draw_checkerboard_background,
    render_text_with_shadow,
)

if TYPE_CHECKING:
    from llm_rpg.scenes.resting_hub.resting_hub_scene import RestingHubScene
    from llm_rpg.systems.hero.hero import Hero
    from llm_rpg.utils.theme import Theme


class RestingHubViewCharacterState(State):
    def __init__(self, resting_hub_scene: RestingHubScene):
        self.resting_hub_scene = resting_hub_scene
        self.current_page: int = 0

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if self.current_page == 0:
                self.current_page = 1
            else:
                self.resting_hub_scene.change_state(RestingHubStates.NAVIGATION)

    def update(self, dt: float):
        pass

    def render(self, screen: pygame.Surface):
        theme = self.resting_hub_scene.game.theme
        hero = self.resting_hub_scene.game.hero
        draw_checkerboard_background(screen, theme)

        if self.current_page == 0:
            self._render_stats_page(screen, hero, theme)
        else:
            self._render_items_page(screen, hero, theme)

    def _render_stats_page(self, screen: pygame.Surface, hero: Hero, theme: Theme):
        spacing = theme.spacing
        margin = spacing(2)
        gap = spacing(2)
        available_width = screen.get_width() - margin * 2
        column_width = (available_width - gap) // 2
        padding = spacing(2)
        line_spacing = spacing(1)

        title_rect = draw_text_panel(
            screen=screen,
            lines="Stats",
            font=theme.fonts["medium"],
            theme=theme,
            y=spacing(4),
            text_color=theme.colors["primary"],
        )

        hero_lines = [
            f"Name: {hero.name}",
            f"Class: {hero.class_name}",
            f"Description: {hero.description}",
        ]
        stats = hero.get_current_stats()
        stats_lines = [
            f"Level: {hero.level}",
            f"Attack: {stats.attack}",
            f"Defense: {stats.defense}",
            f"Focus: {stats.focus}",
            f"HP: {stats.max_hp}",
        ]

        hero_text_size = measure_text_block(
            hero_lines, theme.fonts["small"], line_spacing
        )
        stats_text_size = measure_text_block(
            stats_lines, theme.fonts["small"], line_spacing
        )
        target_height = max(
            hero_text_size[1] + padding * 2,
            stats_text_size[1] + padding * 2,
        )

        top_y = title_rect.bottom + spacing(2)

        hero_rect = draw_text_panel(
            screen=screen,
            lines=hero_lines,
            font=theme.fonts["small"],
            theme=theme,
            x=margin,
            y=top_y,
            width=column_width,
            padding=padding,
            line_spacing=line_spacing,
            align="left",
            auto_wrap=True,
            min_height=target_height,
        )

        draw_text_panel(
            screen=screen,
            lines=stats_lines,
            font=theme.fonts["small"],
            theme=theme,
            x=hero_rect.right + gap,
            y=top_y,
            width=column_width,
            padding=padding,
            line_spacing=line_spacing,
            align="left",
            auto_wrap=True,
            min_height=target_height,
        )

        hint = render_text_with_shadow(
            font=theme.fonts["small"],
            text="Press ENTER to view items",
            color=theme.colors["text_hint"],
            shadow_color=theme.colors["text_hint_shadow"],
        )
        screen.blit(
            hint,
            hint.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - spacing(2))
            ),
        )

    def _render_items_page(self, screen: pygame.Surface, hero: Hero, theme: Theme):
        spacing = theme.spacing
        margin = spacing(2)
        padding = spacing(2)
        line_spacing = spacing(1)
        available_width = screen.get_width() - margin * 2

        title_rect = draw_text_panel(
            screen=screen,
            lines="Items",
            font=theme.fonts["medium"],
            theme=theme,
            y=spacing(4),
            text_color=theme.colors["primary"],
        )

        item_lines = (
            [
                f"* {item.name} ({item.rarity.value}): {item.description}"
                for item in hero.inventory.items
            ]
            if hero.inventory.items
            else ["- None equipped"]
        )

        draw_text_panel(
            screen=screen,
            lines=item_lines,
            font=theme.fonts["small"],
            theme=theme,
            x=margin,
            y=title_rect.bottom + spacing(2),
            width=available_width,
            padding=padding,
            line_spacing=line_spacing,
            align="left",
            auto_wrap=True,
        )
