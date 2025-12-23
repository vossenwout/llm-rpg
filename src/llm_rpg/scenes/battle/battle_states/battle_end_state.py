from __future__ import annotations

import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import PagedTextState
from llm_rpg.ui.battle_ui import render_event_card, render_stats_row

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene


class BattleEndState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.ready_to_exit = False
        self.paged_state = PagedTextState(lines=[])

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN,
            pygame.K_SPACE,
        ):
            self.ready_to_exit = True

    def update(self, dt: float):
        self.battle_scene.update_background(dt)
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
        self.battle_scene.render_background(screen)

        render_stats_row(
            screen=screen,
            theme=self.battle_scene.game.theme,
            hero=self.battle_scene.hero,
            enemy=self.battle_scene.enemy,
        )
        defeated_name = (
            self.battle_scene.enemy.name
            if self.battle_scene.enemy.is_dead()
            else self.battle_scene.hero.name
        )
        message = f"{defeated_name.upper()} WAS DEFEATED!"

        render_event_card(
            screen=screen,
            theme=self.battle_scene.game.theme,
            event=self.battle_scene.latest_event,
            paged_state=self.paged_state,
            text_override=message,
        )
