from dataclasses import dataclass
from llm_rpg.systems.battle.damage_calculator import DamageCalculationResult


@dataclass
class BattleEvent:
    is_hero_turn: bool
    character_name: str
    proposed_action: str
    effect_description: str
    damage_calculation_result: DamageCalculationResult


class BattleLog:
    def __init__(self):
        self.events: list[BattleEvent] = []

    def add_event(self, event: BattleEvent):
        self.events.append(event)

    def get_recent_events(self, n_events: int):
        if n_events <= 0:
            return []
        return self.events[-n_events:]

    def to_string_for_battle_ai(self, n_actions: int = 5):
        battle_log_text = ""
        for event in self.events[-n_actions:]:
            battle_log_text += (
                f"{event.character_name} turn: {event.effect_description}\n"
            )
        return battle_log_text

    def get_string_of_last_events(self, n_events: int, debug_mode: bool = False):
        if len(self.events) == 0:
            return ""
        string_repr = ""
        last_n_events = self.events[-n_events:]
        for i, event in enumerate(last_n_events):
            if event.is_hero_turn:
                string_repr += f"🦸 Your turn:\n {event.character_name} tried to "
            else:
                string_repr += "👾 Enemy turn:\n"
            if debug_mode:
                string_repr += (
                    f"{event.proposed_action}\n\n"
                    f"LLM estimates:\n"
                    f"- feasibility: {event.damage_calculation_result.feasibility}\n"
                    f"- potential damage: {event.damage_calculation_result.potential_damage}\n\n"
                    f"Effect:\n"
                    f"{event.effect_description}\n\n"
                    f"{event.damage_calculation_result.to_string_debug(is_hero_turn=event.is_hero_turn)}\n"
                )
            else:
                string_repr += (
                    f"{event.proposed_action}\n\n"
                    f"LLM estimates:\n"
                    f"- feasibility: {event.damage_calculation_result.feasibility}\n"
                    f"- potential damage: {event.damage_calculation_result.potential_damage}\n\n"
                    f"Effect:\n"
                    f"{event.effect_description}\n\n"
                    f"{event.damage_calculation_result.to_string(is_hero_turn=event.is_hero_turn)}\n"
                )
            if i < len(last_n_events) - 1:
                string_repr += "\n"
        return string_repr
