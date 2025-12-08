from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.battle.battle_states.battle_states import BattleStates
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import draw_text_panel

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

        title = self.battle_scene.game.theme.fonts["medium"].render(
            "An enemy appears", True, self.battle_scene.game.theme.colors["primary"]
        )
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, spacing(8))))

        enemy = self.battle_scene.enemy

        enemy_name = self.battle_scene.game.theme.fonts["medium"].render(
            enemy.name, True, self.battle_scene.game.theme.colors["primary"]
        )
        enemy_name_rect = enemy_name.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 - spacing(3))
        )
        screen.blit(enemy_name, enemy_name_rect)

        description_max_width = screen.get_width() - spacing(6)
        draw_text_panel(
            screen=screen,
            lines=enemy.description,
            font=self.battle_scene.game.theme.fonts["small"],
            theme=self.battle_scene.game.theme,
            x=None,
            y=enemy_name_rect.bottom + spacing(2),
            max_width=description_max_width,
            auto_wrap=True,
            draw_border=False,
        )

        prompt_text = self.battle_scene.game.theme.fonts["small"].render(
            "Press ENTER to start battle",
            True,
            self.battle_scene.game.theme.colors["text_hint"],
        )
        screen.blit(
            prompt_text,
            prompt_text.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - spacing(6))
            ),
        )
