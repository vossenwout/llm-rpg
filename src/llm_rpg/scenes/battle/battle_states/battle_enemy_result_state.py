from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.battle.battle_states.battle_states import BattleStates
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import PagedTextState
from llm_rpg.ui.battle_ui import (
    render_event_card,
    render_event_ribbon,
    render_stats_row,
    render_items_panel,
    render_enemy_sprite,
)

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene
    from llm_rpg.systems.battle.battle_log import BattleEvent


class BattleEnemyResultState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.event: BattleEvent | None = battle_scene.latest_event
        self.paged_state = PagedTextState(lines=[])

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN,
            pygame.K_SPACE,
        ):
            if self.event and not self.paged_state.is_last_page:
                self.paged_state.next_page()
                return
            if self.event and self.battle_scene.hero.is_dead():
                self.battle_scene.change_state(BattleStates.END)
            else:
                self.battle_scene.change_state(BattleStates.TURN)

    def update(self, dt: float):
        return

    def render(self, screen: pygame.Surface):
        screen.fill(self.battle_scene.game.theme.colors["background"])
        render_enemy_sprite(
            screen=screen,
            theme=self.battle_scene.game.theme,
            sprite=self.battle_scene.enemy_sprite,
        )
        render_stats_row(
            screen=screen,
            theme=self.battle_scene.game.theme,
            hero=self.battle_scene.hero,
            enemy=self.battle_scene.enemy,
        )
        render_items_panel(
            screen=screen,
            theme=self.battle_scene.game.theme,
            hero=self.battle_scene.hero,
            proc_impacts=None,
        )
        if self.event:
            card_rect = render_event_card(
                screen=screen,
                theme=self.battle_scene.game.theme,
                event=self.event,
                paged_state=self.paged_state,
            )
            render_event_ribbon(
                screen=screen,
                theme=self.battle_scene.game.theme,
                event=self.event,
                card_rect=card_rect,
            )
