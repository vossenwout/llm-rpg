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
    render_enemy_sprite,
)

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene
    from llm_rpg.systems.battle.battle_log import BattleEvent


class BattleHeroResultState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.event: BattleEvent | None = battle_scene.latest_event
        self.paged_state = PagedTextState(lines=[])

    def _build_proc_impacts(self) -> dict[str, int]:
        if not self.event:
            return {}
        impacts: dict[str, int] = {}
        for (
            bonus
        ) in self.event.damage_calculation_result.applied_bonus_multiplier_damages:
            name = bonus.bonus_multiplier.item_name
            impacts[name] = impacts.get(name, 0) + bonus.damage_impact
        return impacts

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_RETURN,
            pygame.K_SPACE,
        ):
            if self.event and not self.paged_state.is_last_page:
                self.paged_state.next_page()
                return
            if self.event and not self.battle_scene.enemy.is_dead():
                self.battle_scene.change_state(BattleStates.ENEMY_THINKING)
            else:
                self.battle_scene.change_state(BattleStates.END)

    def update(self, dt: float):
        self.battle_scene.update_background(dt)
        return

    def render(self, screen: pygame.Surface):
        self.battle_scene.render_background(screen)
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
