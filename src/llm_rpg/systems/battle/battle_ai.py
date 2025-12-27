from dataclasses import dataclass

from llm_rpg.systems.battle.action_judges import ActionJudge, ActionJudgment
from llm_rpg.systems.battle.action_narrators import ActionNarrator
from llm_rpg.systems.battle.enemy import Enemy
from llm_rpg.systems.hero.hero import Hero


@dataclass(frozen=True)
class ActionEffect:
    feasibility: float
    potential_damage: float
    effect_description: str


class BattleAI:
    def __init__(
        self,
        action_judge: ActionJudge,
        action_narrator: ActionNarrator,
        debug: bool = False,
    ):
        self.action_judge = action_judge
        self.action_narrator = action_narrator
        self.debug = debug

    def determine_action_judgment(
        self,
        proposed_action_attacker: str,
        hero: Hero,
        enemy: Enemy,
        is_hero_attacker: bool,
        battle_log_string: str,
    ) -> ActionJudgment:
        return self.action_judge.judge_action(
            proposed_action_attacker=proposed_action_attacker,
            hero=hero,
            enemy=enemy,
            is_hero_attacker=is_hero_attacker,
            battle_log_string=battle_log_string,
        )

    def describe_action(
        self,
        proposed_action_attacker: str,
        hero: Hero,
        enemy: Enemy,
        is_hero_attacker: bool,
        battle_log_string: str,
        judgment: ActionJudgment,
        total_damage: int,
    ) -> ActionEffect:
        effect_description = self.action_narrator.describe_action(
            proposed_action_attacker=proposed_action_attacker,
            hero=hero,
            enemy=enemy,
            is_hero_attacker=is_hero_attacker,
            battle_log_string=battle_log_string,
            judgment=ActionJudgment(
                feasibility=judgment.feasibility,
                potential_damage=judgment.potential_damage,
            ),
            total_damage=total_damage,
        )
        return ActionEffect(
            feasibility=judgment.feasibility,
            potential_damage=judgment.potential_damage,
            effect_description=effect_description,
        )
