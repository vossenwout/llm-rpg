from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.battle.battle_states.battle_states import BattleStates
from llm_rpg.scenes.state import State
from llm_rpg.ui.battle_ui import draw_hp_bar
from llm_rpg.ui.components import draw_panel

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene


class BattleStartState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.ready_to_start = False

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.ready_to_start = True

    def update(self, dt: float):
        if self.ready_to_start:
            self.battle_scene.change_state(BattleStates.TURN)

    def render(self, screen: pygame.Surface):
        screen.fill(self.battle_scene.game.theme.colors["background"])
        spacing = self.battle_scene.game.theme.spacing

        title = self.battle_scene.game.theme.fonts["title"].render(
            "Battle Start", True, self.battle_scene.game.theme.colors["primary"]
        )
        screen.blit(
            title, title.get_rect(center=(screen.get_width() // 2, spacing(1.5)))
        )

        hero_panel = pygame.Rect(spacing(1), spacing(3), spacing(8), spacing(5))
        enemy_panel = pygame.Rect(
            screen.get_width() - spacing(1) - spacing(8),
            spacing(3),
            spacing(8),
            spacing(5),
        )
        draw_panel(screen, hero_panel, self.battle_scene.game.theme)
        draw_panel(screen, enemy_panel, self.battle_scene.game.theme)

        hero = self.battle_scene.hero
        enemy = self.battle_scene.enemy

        hero_text = self.battle_scene.game.theme.fonts["large"].render(
            hero.name or "Hero", True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(
            hero_text,
            hero_text.get_rect(center=(hero_panel.centerx, hero_panel.y + spacing(1))),
        )
        draw_hp_bar(
            screen=screen,
            theme=self.battle_scene.game.theme,
            x=hero_panel.x + spacing(1),
            y=hero_panel.y + spacing(2.5),
            hp=hero.hp,
            max_hp=hero.get_current_stats().max_hp,
            width=spacing(6),
        )

        enemy_text = self.battle_scene.game.theme.fonts["large"].render(
            enemy.name, True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(
            enemy_text,
            enemy_text.get_rect(
                center=(enemy_panel.centerx, enemy_panel.y + spacing(1))
            ),
        )
        draw_hp_bar(
            screen=screen,
            theme=self.battle_scene.game.theme,
            x=enemy_panel.x + spacing(1),
            y=enemy_panel.y + spacing(2.5),
            hp=enemy.hp,
            max_hp=enemy.get_current_stats().max_hp,
            width=spacing(6),
        )

        vs_text = self.battle_scene.game.theme.fonts["large"].render(
            "VS", True, self.battle_scene.game.theme.colors["primary"]
        )
        screen.blit(
            vs_text, vs_text.get_rect(center=(screen.get_width() // 2, spacing(4)))
        )

        subtitle = self.battle_scene.game.theme.fonts["small"].render(
            "Press Enter to start",
            True,
            self.battle_scene.game.theme.colors["text_hint"],
        )
        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - spacing(1.5))
            ),
        )
