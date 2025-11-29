from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene


class BattleEndState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.timer = 0.8  # brief pause before transitioning

    def handle_input(self, event: pygame.event.Event):
        # No input required during end screen
        pass

    def update(self, dt: float):
        self.timer -= dt
        if self.timer > 0:
            return

        if not self.battle_scene.hero.is_dead():
            self.battle_scene.game.battles_won += 1
            if self.battle_scene.game.battles_won % 2 == 0:
                self.battle_scene.hero.discovered_item = True
            if self.battle_scene.game.battles_won % 2 == 1:
                self.battle_scene.hero.should_level_up = True
            self.battle_scene.hero.full_heal()
            self.battle_scene.game.change_scene(SceneTypes.RESTING_HUB)
        else:
            self.battle_scene.game.change_scene(SceneTypes.GAME_OVER)

    def _draw_hp_bar(
        self, screen: pygame.Surface, x: int, y: int, hp: int, max_hp: int
    ):
        bar_width = 200
        bar_height = 16
        pct = max(hp, 0) / max(max_hp, 1)
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x, y, int(bar_width * pct), bar_height)
        pygame.draw.rect(
            screen, self.battle_scene.game.theme.colors["text"], outline_rect, 2
        )
        pygame.draw.rect(screen, (80, 200, 120), fill_rect)

    def render(self, screen: pygame.Surface):
        screen.fill(self.battle_scene.game.theme.colors["background"])

        title_text = self.battle_scene.game.theme.fonts["title"].render(
            "Battle Ended", True, self.battle_scene.game.theme.colors["primary"]
        )
        screen.blit(
            title_text, title_text.get_rect(center=(screen.get_width() // 2, 70))
        )

        winner = (
            self.battle_scene.hero.name
            if not self.battle_scene.hero.is_dead()
            else self.battle_scene.enemy.name
        )
        outcome_text = self.battle_scene.game.theme.fonts["large"].render(
            f"{winner} won!", True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(
            outcome_text, outcome_text.get_rect(center=(screen.get_width() // 2, 130))
        )

        hero = self.battle_scene.hero
        enemy = self.battle_scene.enemy

        # Recent events (current turn only)
        if self.battle_scene.battle_log.events:
            log_text = self.battle_scene.battle_log.get_string_of_last_events(
                n_events=2, debug_mode=self.battle_scene.game.config.debug_mode
            )
            for i, line in enumerate(log_text.splitlines()):
                surf = self.battle_scene.game.theme.fonts["small"].render(
                    line, True, self.battle_scene.game.theme.colors["text"]
                )
                screen.blit(surf, (60, 200 + i * 22))

        # Stats
        hero_label = self.battle_scene.game.theme.fonts["medium"].render(
            hero.name or "Hero", True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(hero_label, (60, 280))
        self._draw_hp_bar(screen, 60, 310, hero.hp, hero.get_current_stats().max_hp)

        enemy_label = self.battle_scene.game.theme.fonts["medium"].render(
            enemy.name, True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(enemy_label, (60, 360))
        self._draw_hp_bar(screen, 60, 390, enemy.hp, enemy.get_current_stats().max_hp)

        hint = self.battle_scene.game.theme.fonts["small"].render(
            "Preparing next scene...",
            True,
            self.battle_scene.game.theme.colors["text_hint"],
        )
        screen.blit(
            hint,
            hint.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40)),
        )
