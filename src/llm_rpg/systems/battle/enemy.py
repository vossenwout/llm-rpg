from enum import Enum

from llm_rpg.objects.character import Character, Stats
from llm_rpg.systems.battle.enemy_action_generators import EnemyActionGenerator
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
        archetype: EnemyArchetypes,
        enemy_action_generator: EnemyActionGenerator,
    ):
        super().__init__(
            name=name, description=description, level=level, base_stats=base_stats
        )
        self.archetype = archetype
        self.enemy_action_generator = enemy_action_generator

    def get_current_stats(self) -> Stats:
        return self.base_stats

    def get_next_action(self, battle_log: BattleLog, hero: Hero) -> str:
        return self.enemy_action_generator.generate_next_action(
            enemy=self, hero=hero, battle_log=battle_log
        )
