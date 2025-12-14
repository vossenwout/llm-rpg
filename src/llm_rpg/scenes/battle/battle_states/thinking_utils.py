from __future__ import annotations
import queue
from typing import TypedDict, Literal

from llm_rpg.systems.battle.battle_log import BattleEvent
from llm_rpg.systems.battle.damage_calculator import DamageCalculationResult


class Outcome(TypedDict):
    target: Literal["enemy", "hero"]
    damage: int
    event: BattleEvent
    success: bool
    message: str


def make_error_outcome(
    is_hero_turn: bool,
    actor_name: str,
    message: str,
) -> Outcome:
    dmg_result = DamageCalculationResult(
        random_factor=0,
        base_dmg=0,
        applied_feasibility_boosts=[],
        applied_potential_damage_boosts=[],
        feasibility=0,
        potential_damage=0,
        llm_dmg_impact=0,
        llm_dmg_scaling=0,
        llm_scaled_base_dmg=0,
        answer_speed_s=0,
        n_new_words_in_action=0,
        n_overused_words_in_action=0,
        applied_bonus_multiplier_damages=[],
        total_dmg=0,
    )
    event = BattleEvent(
        is_hero_turn=is_hero_turn,
        character_name=actor_name,
        proposed_action="...",
        effect_description="The action failed.",
        damage_calculation_result=dmg_result,
    )
    return {
        "target": "enemy" if is_hero_turn else "hero",
        "damage": 0,
        "event": event,
        "success": False,
        "message": message,
    }


def push_result(q: "queue.Queue[Outcome]", outcome: Outcome):
    q.put(outcome)


def pop_result(q: "queue.Queue[Outcome]"):
    if q.empty():
        return None
    return q.get_nowait()


def has_timed_out(elapsed: float, max_wait: float):
    return elapsed >= max_wait


def apply_outcome(outcome: Outcome, battle_scene):
    if outcome["target"] == "enemy":
        battle_scene.enemy.inflict_damage(outcome["damage"])
    else:
        battle_scene.hero.inflict_damage(outcome["damage"])
    if outcome["event"].is_hero_turn:
        battle_scene.creativity_tracker.add_action(outcome["event"].proposed_action)
    battle_scene.battle_log.add_event(outcome["event"])
    battle_scene.latest_event = outcome["event"]
