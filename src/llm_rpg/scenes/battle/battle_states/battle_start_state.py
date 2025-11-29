from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.battle.battle_states.battle_states import BattleStates
from llm_rpg.scenes.state import State

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

    def _draw_hp_bar(
        self, screen: pygame.Surface, x: int, y: int, hp: int, max_hp: int
    ):
        bar_width = 220
        bar_height = 18
        pct = max(hp, 0) / max(max_hp, 1)
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x, y, int(bar_width * pct), bar_height)
        pygame.draw.rect(
            screen, self.battle_scene.game.theme.colors["text"], outline_rect, 2
        )
        pygame.draw.rect(screen, (80, 200, 120), fill_rect)

    def render(self, screen: pygame.Surface):
        screen.fill(self.battle_scene.game.theme.colors["background"])

        title = self.battle_scene.game.theme.fonts["title"].render(
            "Battle Start", True, self.battle_scene.game.theme.colors["primary"]
        )
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 70)))

        vs_text = self.battle_scene.game.theme.fonts["large"].render(
            "VS", True, self.battle_scene.game.theme.colors["text"]
        )

        # Hero info
        hero = self.battle_scene.hero
        hero_text = self.battle_scene.game.theme.fonts["large"].render(
            hero.name or "Hero", True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(
            hero_text, hero_text.get_rect(center=(screen.get_width() * 0.25, 200))
        )
        self._draw_hp_bar(
            screen,
            int(screen.get_width() * 0.15),
            250,
            hero.hp,
            hero.get_current_stats().max_hp,
        )

        # Enemy info
        enemy = self.battle_scene.enemy
        enemy_text = self.battle_scene.game.theme.fonts["large"].render(
            enemy.name, True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(
            enemy_text, enemy_text.get_rect(center=(screen.get_width() * 0.75, 200))
        )
        self._draw_hp_bar(
            screen,
            int(screen.get_width() * 0.65),
            250,
            enemy.hp,
            enemy.get_current_stats().max_hp,
        )

        # VS in the middle
        screen.blit(vs_text, vs_text.get_rect(center=(screen.get_width() // 2, 220)))

        subtitle = self.battle_scene.game.theme.fonts["small"].render(
            "Press Enter to start",
            True,
            self.battle_scene.game.theme.colors["text_hint"],
        )
        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - 80)
            ),
        )
