from __future__ import annotations
import threading
import queue
import pygame
from typing import TYPE_CHECKING, Literal, TypedDict, Optional

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
    push_result,
    pop_result,
    has_timed_out,
    apply_outcome,
)

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene
    from llm_rpg.systems.hero.hero import ProposedHeroAction


class ProcessingOutcome(TypedDict):
    target: Literal["enemy", "hero"]
    damage: int
    event: BattleEvent
    success: bool
    message: str


class BattleHeroThinkingState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.proposed_action: Optional[ProposedHeroAction] = (
            battle_scene.pending_hero_action
        )
        self.battle_scene.pending_hero_action = None
        self.animation_timer = 0.0
        self.dot_timer = 0.0
        self.dots = 0
        self.processing_started = False
        self.processing_done = False
        self.pending_outcome: Optional[Outcome] = None
        self.minimum_display = 0.25
        self.max_wait = 60.0
        self.result_queue: queue.Queue[Outcome] = queue.Queue(maxsize=1)
        self.ui_cfg = BattleUIConfig()
        self.error_message = ""

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
                is_hero_turn=True,
                actor_name=self.battle_scene.hero.name,
                message="Timed out while thinking.",
            )

        if (
            self.processing_done
            and self.pending_outcome is not None
            and self.animation_timer >= self.minimum_display
        ):
            if not self.pending_outcome["success"]:
                self.error_message = self.pending_outcome["message"]
            self._apply_outcome()
            self.battle_scene.change_state(BattleStates.HERO_RESULT)

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
            text="Hero is thinking",
            dots=self.dots,
        )
        if self.error_message:
            error_surface = self.battle_scene.game.theme.fonts["small"].render(
                self.error_message,
                True,
                (255, 60, 60),
            )
            screen.blit(
                error_surface,
                error_surface.get_rect(
                    center=(
                        screen.get_width() // 2,
                        screen.get_height() - self.battle_scene.game.theme.spacing(1),
                    )
                ),
            )

    def _process_action(self):
        try:
            if self.proposed_action is None:
                outcome = self._build_error_outcome("No action provided.")
                self.result_queue.put(outcome)
                self.processing_done = True
                return

            action_effect = self.battle_scene.battle_ai.determine_action_effect(
                proposed_action_attacker=self.proposed_action.action,
                hero=self.battle_scene.hero,
                enemy=self.battle_scene.enemy,
                is_hero_attacker=True,
                battle_log_string=self.battle_scene.battle_log.to_string_for_battle_ai(),
            )

            n_new_words_in_action = (
                self.battle_scene.creativity_tracker.count_new_words_in_action(
                    action=self.proposed_action.action
                )
            )
            n_overused_words_in_action = (
                self.battle_scene.creativity_tracker.count_overused_words_in_action(
                    action=self.proposed_action.action
                )
            )
            damage_calculation_result = (
                self.battle_scene.damage_calculator.calculate_damage(
                    attack=self.battle_scene.hero.get_current_stats().attack,
                    defense=self.battle_scene.enemy.get_current_stats().defense,
                    feasibility=action_effect.feasibility,
                    potential_damage=action_effect.potential_damage,
                    n_new_words_in_action=n_new_words_in_action,
                    n_overused_words_in_action=n_overused_words_in_action,
                    answer_speed_s=self.proposed_action.time_to_answer_seconds,
                    equiped_items=self.battle_scene.hero.inventory.items,
                )
            )
            outcome: ProcessingOutcome = {
                "target": "enemy",
                "damage": damage_calculation_result.total_dmg,
                "event": BattleEvent(
                    is_hero_turn=True,
                    character_name=self.battle_scene.hero.name,
                    proposed_action=self.proposed_action.action,
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
                    is_hero_turn=True,
                    actor_name=self.battle_scene.hero.name,
                    message=str(exc),
                ),
            )
        self.processing_done = True

    def _apply_outcome(self):
        if not self.pending_outcome:
            return
        apply_outcome(self.pending_outcome, self.battle_scene)
        self.pending_outcome = None
        self.result_ready = False
