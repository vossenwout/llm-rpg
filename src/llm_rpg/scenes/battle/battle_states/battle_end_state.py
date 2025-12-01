from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State
from llm_rpg.ui.battle_ui import draw_hp_bar

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene


class BattleEndState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.ready_to_exit = False

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN,
            pygame.K_SPACE,
        ):
            self.ready_to_exit = True

    def update(self, dt: float):
        if not self.ready_to_exit:
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

        # Stats
        hero_label = self.battle_scene.game.theme.fonts["medium"].render(
            hero.name or "Hero", True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(hero_label, (60, 280))
        draw_hp_bar(
            screen=screen,
            theme=self.battle_scene.game.theme,
            x=60,
            y=310,
            hp=hero.hp,
            max_hp=hero.get_current_stats().max_hp,
            width=200,
        )

        enemy_label = self.battle_scene.game.theme.fonts["medium"].render(
            enemy.name, True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(enemy_label, (60, 360))
        draw_hp_bar(
            screen=screen,
            theme=self.battle_scene.game.theme,
            x=60,
            y=390,
            hp=enemy.hp,
            max_hp=enemy.get_current_stats().max_hp,
            width=200,
        )

        hint = self.battle_scene.game.theme.fonts["small"].render(
            "Press Enter to continue",
            True,
            self.battle_scene.game.theme.colors["text_hint"],
        )
        screen.blit(
            hint,
            hint.get_rect(center=(screen.get_width() // 2, screen.get_height() - 40)),
        )
