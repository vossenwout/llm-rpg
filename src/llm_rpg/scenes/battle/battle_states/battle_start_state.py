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

    def render(self, screen: pygame.Surface):
        screen.fill(self.battle_scene.game.theme.colors["background"])
        spacing = self.battle_scene.game.theme.spacing

        title = self.battle_scene.game.theme.fonts["large"].render(
            "Battle Start", True, self.battle_scene.game.theme.colors["primary"]
        )
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, spacing(8))))

        hero = self.battle_scene.hero
        enemy = self.battle_scene.enemy

        hero_text = self.battle_scene.game.theme.fonts["small"].render(
            hero.name, True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(
            hero_text,
            hero_text.get_rect(center=(spacing(8), screen.get_height() // 2)),
        )

        enemy_text = self.battle_scene.game.theme.fonts["small"].render(
            enemy.name, True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(
            enemy_text,
            enemy_text.get_rect(
                center=(screen.get_width() - spacing(8), screen.get_height() // 2)
            ),
        )

        vs_text = self.battle_scene.game.theme.fonts["medium"].render(
            "VS", True, self.battle_scene.game.theme.colors["primary"]
        )
        screen.blit(
            vs_text,
            vs_text.get_rect(
                center=(screen.get_width() // 2, screen.get_height() // 2)
            ),
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
