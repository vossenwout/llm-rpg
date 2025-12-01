from enum import Enum

from llm_rpg.llm.llm import LLM
from llm_rpg.objects.character import Character, Stats
from llm_rpg.systems.hero.hero import Hero
from llm_rpg.systems.battle.battle_log import BattleLog


class EnemyArchetypes(Enum):
    DEFENDER = "defender"
    ATTACKER = "attacker"
    TANK = "tank"


class Enemy(Character):
    def __init__(
        self,
        name: str,
        description: str,
        level: int,
        base_stats: Stats,
        llm: LLM,
        archetype: EnemyArchetypes,
        ascii_render: str,
        enemy_next_action_prompt: str,
    ):
        super().__init__(
            name=name, description=description, level=level, base_stats=base_stats
        )
        self.llm = llm
        self.archetype = archetype
        self.ascii_render = ascii_render
        self.enemy_next_action_prompt = enemy_next_action_prompt

    def get_current_stats(self) -> Stats:
        return self.base_stats

    def get_next_action(self, battle_log: BattleLog, hero: Hero):
        battle_log_string = battle_log.to_string_for_battle_ai()

        prompt = self.enemy_next_action_prompt.format(
            self_name=self.name,
            self_description=self.description,
            self_max_hp=self.get_current_stats().max_hp,
            hero_name=hero.name,
            hero_description=hero.description,
            hero_max_hp=hero.get_current_stats().max_hp,
            battle_log_string=battle_log_string,
        )

        return self.llm.generate_completion(prompt)
