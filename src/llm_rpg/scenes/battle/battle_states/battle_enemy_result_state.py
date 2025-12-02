from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.battle.battle_states.battle_states import BattleStates
from llm_rpg.scenes.state import State
from llm_rpg.ui.battle_ui import (
    render_event_card,
    render_stats_row,
    prompt_for_battle_end,
)

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene
    from llm_rpg.systems.battle.battle_log import BattleEvent


class BattleEnemyResultState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.event: BattleEvent | None = battle_scene.latest_event

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN,
            pygame.K_SPACE,
        ):
            if self.event and self.battle_scene.hero.is_dead():
                self.battle_scene.change_state(BattleStates.END)
            else:
                self.battle_scene.change_state(BattleStates.TURN)

    def update(self, dt: float):
        return

    def render(self, screen: pygame.Surface):
        screen.fill(self.battle_scene.game.theme.colors["background"])
        render_stats_row(
            screen=screen,
            theme=self.battle_scene.game.theme,
            hero=self.battle_scene.hero,
            enemy=self.battle_scene.enemy,
        )
        if self.event:
            prompt = prompt_for_battle_end(
                is_finishing=bool(self.event and self.battle_scene.hero.is_dead())
            )
            render_event_card(
                screen=screen,
                theme=self.battle_scene.game.theme,
                event=self.event,
                panel_x=40,
                panel_y=screen.get_height() - 180,
                panel_width=screen.get_width() - 80,
                debug_mode=self.battle_scene.game.config.debug_mode,
                prompt_text=prompt,
            )
