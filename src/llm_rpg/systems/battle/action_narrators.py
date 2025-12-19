from __future__ import annotations

from abc import ABC, abstractmethod

from llm_rpg.llm.llm import LLM
from llm_rpg.objects.item import Item
from llm_rpg.systems.battle.action_judges import ActionJudgment
from llm_rpg.systems.battle.enemy import Enemy
from llm_rpg.systems.hero.hero import Hero


class ActionNarrator(ABC):
    @abstractmethod
    def describe_action(
        self,
        proposed_action_attacker: str,
        hero: Hero,
        enemy: Enemy,
        is_hero_attacker: bool,
        battle_log_string: str,
        judgment: ActionJudgment,
        total_damage: int,
    ) -> str:
        raise NotImplementedError


class LLMActionNarrator(ActionNarrator):
    def __init__(self, llm: LLM, prompt: str, debug: bool = False):
        self.llm = llm
        self.prompt = prompt
        self.debug = debug

    def _format_items(self, items: list[Item]) -> str:
        return "\n".join([f"  - {item.name}: {item.description}" for item in items])

    def _get_prompt(
        self,
        hero: Hero,
        enemy: Enemy,
        is_hero_attacker: bool,
        battle_log_string: str,
        proposed_action_attacker: str,
        judgment: ActionJudgment,
        total_damage: int,
    ) -> str:
        items_hero = self._format_items(hero.inventory.items)
        hero_name = hero.name
        if is_hero_attacker:
            attacker_name = hero.name
            defender_name = enemy.name
            attacker_description = hero.description
            defender_description = enemy.description
        else:
            attacker_name = enemy.name
            defender_name = hero.name
            attacker_description = enemy.description
            defender_description = hero.description
        return self.prompt.format(
            attacker_name=attacker_name,
            defender_name=defender_name,
            attacker_description=attacker_description,
            defender_description=defender_description,
            hero_name=hero_name,
            items_hero=items_hero,
            battle_log_string=battle_log_string,
            proposed_action_attacker=proposed_action_attacker,
            feasibility=judgment.feasibility,
            potential_damage=judgment.potential_damage,
            total_damage=total_damage,
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
    ) -> str:
        prompt = self._get_prompt(
            hero=hero,
            enemy=enemy,
            is_hero_attacker=is_hero_attacker,
            battle_log_string=battle_log_string,
            proposed_action_attacker=proposed_action_attacker,
            judgment=judgment,
            total_damage=total_damage,
        )
        if self.debug:
            print("////////////DEBUG ActionNarrator prompt////////////")
            print(prompt)
            print("////////////DEBUG ActionNarrator prompt////////////")
        return self.llm.generate_completion(prompt=prompt)
