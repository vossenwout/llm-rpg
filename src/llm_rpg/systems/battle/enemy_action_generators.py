from __future__ import annotations

from abc import ABC, abstractmethod

from llm_rpg.llm.llm import LLM
from typing import TYPE_CHECKING

from llm_rpg.systems.battle.battle_log import BattleLog

if TYPE_CHECKING:
    from llm_rpg.systems.battle.enemy import Enemy
    from llm_rpg.systems.hero.hero import Hero


class EnemyActionGenerator(ABC):
    @abstractmethod
    def generate_next_action(
        self, enemy: Enemy, hero: Hero, battle_log: BattleLog
    ) -> str:
        raise NotImplementedError


class LLMEnemyActionGenerator(EnemyActionGenerator):
    def __init__(self, llm: LLM, prompt: str, debug: bool = False):
        self.llm = llm
        self.prompt = prompt
        self.debug = debug

    def generate_next_action(
        self, enemy: Enemy, hero: Hero, battle_log: BattleLog
    ) -> str:
        battle_log_string = battle_log.to_string_for_battle_ai()
        prompt = self.prompt.format(
            self_name=enemy.name,
            self_description=enemy.description,
            self_max_hp=enemy.get_current_stats().max_hp,
            hero_name=hero.name,
            hero_description=hero.description,
            hero_max_hp=hero.get_current_stats().max_hp,
            battle_log_string=battle_log_string,
        )
        if self.debug:
            print("////////////DEBUG EnemyAction prompt////////////")
            print(prompt)
            print("////////////DEBUG EnemyAction prompt////////////")
        return self.llm.generate_completion(prompt)
