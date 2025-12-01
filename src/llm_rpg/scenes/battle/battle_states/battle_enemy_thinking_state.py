from __future__ import annotations
import threading
import queue
import pygame
from typing import TYPE_CHECKING, Literal, TypedDict

from llm_rpg.scenes.battle.battle_states.battle_states import BattleStates
from llm_rpg.scenes.state import State
from llm_rpg.systems.battle.battle_log import BattleEvent
from llm_rpg.ui.battle_ui import (
    render_stats_row,
    advance_dots,
    BattleUIConfig,
    render_processing_text,
)
from llm_rpg.scenes.battle.battle_states.thinking_utils import (
    Outcome,
    make_error_outcome,
    pop_result,
    push_result,
    has_timed_out,
    apply_outcome,
)

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene


class EnemyProcessingOutcome(TypedDict):
    target: Literal["hero"]
    damage: int
    event: BattleEvent
    success: bool
    message: str


class BattleEnemyThinkingState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.animation_timer = 0.0
        self.dot_timer = 0.0
        self.dots = 0
        self.processing_started = False
        self.processing_done = False
        self.pending_outcome: Outcome | None = None
        self.minimum_display = 0.25
        self.max_wait = 20.0
        self.result_queue: queue.Queue[Outcome] = queue.Queue(maxsize=1)
        self.ui_cfg = BattleUIConfig()

    def handle_input(self, event: pygame.event.Event):
        return

    def update(self, dt: float):
        self.animation_timer += dt
        self.dots, self.dot_timer = advance_dots(
            dots=self.dots,
            dot_timer=self.dot_timer,
            dt=dt,
            period=self.ui_cfg.dots_period,
        )

        if not self.processing_started:
            self.processing_started = True
            thread = threading.Thread(target=self._process_action, daemon=True)
            thread.start()

        if self.pending_outcome is None:
            pending = pop_result(self.result_queue)
            if pending:
                self.pending_outcome = pending

        if self.pending_outcome is None and has_timed_out(
            self.animation_timer, self.max_wait
        ):
            self.pending_outcome = make_error_outcome(
                is_hero_turn=False,
                actor_name=self.battle_scene.enemy.name,
                message="Timed out while thinking.",
            )

        if (
            self.processing_done
            and self.pending_outcome is not None
            and self.animation_timer >= self.minimum_display
        ):
            self._apply_outcome()
            self.battle_scene.change_state(BattleStates.ENEMY_RESULT)

    def render(self, screen: pygame.Surface):
        screen.fill(self.battle_scene.game.theme.colors["background"])
        render_stats_row(
            screen=screen,
            theme=self.battle_scene.game.theme,
            hero=self.battle_scene.hero,
            enemy=self.battle_scene.enemy,
            config=self.ui_cfg,
        )
        render_processing_text(
            screen=screen,
            theme=self.battle_scene.game.theme,
            text="Enemy is plotting",
            dots=self.dots,
        )

    def _process_action(self):
        try:
            proposed_enemy_action = self.battle_scene.enemy.get_next_action(
                self.battle_scene.battle_log, self.battle_scene.hero
            )
            action_effect = self.battle_scene.battle_ai.determine_action_effect(
                proposed_action_attacker=proposed_enemy_action,
                hero=self.battle_scene.hero,
                enemy=self.battle_scene.enemy,
                is_hero_attacker=False,
                battle_log_string=self.battle_scene.battle_log.to_string_for_battle_ai(),
            )
            damage_calculation_result = (
                self.battle_scene.damage_calculator.calculate_damage(
                    attack=self.battle_scene.enemy.get_current_stats().attack,
                    defense=self.battle_scene.hero.get_current_stats().defense,
                    feasibility=action_effect.feasibility,
                    potential_damage=action_effect.potential_damage,
                    n_new_words_in_action=0,
                    n_overused_words_in_action=0,
                    answer_speed_s=1000,
                    equiped_items=[],
                )
            )
            outcome: EnemyProcessingOutcome = {
                "target": "hero",
                "damage": damage_calculation_result.total_dmg,
                "event": BattleEvent(
                    is_hero_turn=False,
                    character_name=self.battle_scene.enemy.name,
                    proposed_action=proposed_enemy_action,
                    effect_description=action_effect.effect_description,
                    damage_calculation_result=damage_calculation_result,
                ),
                "success": True,
                "message": "",
            }
            self.result_queue.put(outcome)
        except Exception as exc:
            push_result(
                self.result_queue,
                make_error_outcome(
                    is_hero_turn=False,
                    actor_name=self.battle_scene.enemy.name,
                    message=str(exc),
                ),
            )
        self.processing_done = True

    def _apply_outcome(self):
        if not self.pending_outcome:
            return
        apply_outcome(self.pending_outcome, self.battle_scene)
        self.pending_outcome = None
