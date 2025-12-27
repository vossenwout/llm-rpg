from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from typing import Annotated

from pydantic import BaseModel, Field

from llm_rpg.llm.llm import LLM
from llm_rpg.objects.item import Item
from llm_rpg.systems.battle.enemy import Enemy
from llm_rpg.systems.hero.hero import Hero


@dataclass(frozen=True)
class ActionJudgment:
    feasibility: float
    potential_damage: float


class ActionJudge(ABC):
    @abstractmethod
    def judge_action(
        self,
        proposed_action_attacker: str,
        hero: Hero,
        enemy: Enemy,
        is_hero_attacker: bool,
        battle_log_string: str,
    ) -> ActionJudgment:
        raise NotImplementedError


class LLMActionJudgmentOutput(BaseModel):
    feasibility: Annotated[
        float,
        Field(
            ge=0,
            le=10,
            description=(
                "How feasible the action is, ranging from 0 to 10. A value of 0 indicates the action is "
                "completely infeasible, while a value of 10 indicates it is fully feasible."
            ),
        ),
    ]
    potential_damage: Annotated[
        float,
        Field(
            ge=0,
            le=10,
            description=(
                "Potential damage the action can inflict, ranging from 0 to 10. A score of 0 means the action "
                "causes no damage, whereas a score of 10 means it causes maximum possible damage."
            ),
        ),
    ]


class LLMActionJudge(ActionJudge):
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
        prompt = self.prompt.format(
            attacker_name=attacker_name,
            defender_name=defender_name,
            attacker_description=attacker_description,
            defender_description=defender_description,
            hero_name=hero_name,
            items_hero=items_hero,
            battle_log_string=battle_log_string,
            proposed_action_attacker=proposed_action_attacker,
        )
        schema = json.dumps(LLMActionJudgmentOutput.model_json_schema(), indent=2)
        return f"{prompt}{schema}"

    def judge_action(
        self,
        proposed_action_attacker: str,
        hero: Hero,
        enemy: Enemy,
        is_hero_attacker: bool,
        battle_log_string: str,
    ) -> ActionJudgment:
        attempts = 0
        while attempts < 3:
            prompt = self._get_prompt(
                hero=hero,
                enemy=enemy,
                is_hero_attacker=is_hero_attacker,
                battle_log_string=battle_log_string,
                proposed_action_attacker=proposed_action_attacker,
            )
            if self.debug:
                print("////////////DEBUG ActionJudge prompt////////////")
                print(prompt)
                print("////////////DEBUG ActionJudge prompt////////////")
            try:
                unscaled_output = self.llm.generate_structured_completion(
                    prompt=prompt, output_model=LLMActionJudgmentOutput
                )
                return ActionJudgment(
                    feasibility=unscaled_output.feasibility / 10,
                    potential_damage=unscaled_output.potential_damage / 10,
                )
            except Exception as exc:
                print(exc)
                attempts += 1
                continue
        raise ValueError("Failed to determine action judgment")


class TransformersActionJudge(ActionJudge):
    def __init__(self, model_name: str, device: str = "cpu"):
        self.model_name = model_name
        self.device = device

    def judge_action(
        self,
        proposed_action_attacker: str,
        hero: Hero,
        enemy: Enemy,
        is_hero_attacker: bool,
        battle_log_string: str,
    ) -> ActionJudgment:
        raise NotImplementedError("TransformersActionJudge is not implemented yet")
