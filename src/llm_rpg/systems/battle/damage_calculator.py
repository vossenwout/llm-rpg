from __future__ import annotations
from dataclasses import dataclass
from math import ceil, floor
import random
from typing import List, Tuple, TYPE_CHECKING


from llm_rpg.objects.item import (
    BonusMultiplier,
    Item,
    LLMScalingBoost,
)

if TYPE_CHECKING:
    from llm_rpg.game.game_config import GameConfig


@dataclass
class DamageCalculationConfig:
    ad_diff_scaling: float
    ad_parity_dmg: float
    random_factor_max: float
    random_factor_min: float
    llm_dmg_impact: int


@dataclass
class BonusMultiplierDamage:
    bonus_multiplier: BonusMultiplier
    damage_impact: int


class DamageCalculationResult:
    def __init__(
        self,
        random_factor: float,
        base_dmg: float,
        applied_feasibility_boosts: List[LLMScalingBoost],
        applied_potential_damage_boosts: List[LLMScalingBoost],
        feasibility: float,
        potential_damage: float,
        llm_dmg_impact: float,
        llm_dmg_scaling: float,
        llm_scaled_base_dmg: float,
        answer_speed_s: float,
        n_new_words_in_action: int,
        n_overused_words_in_action: int,
        applied_bonus_multiplier_damages: List[BonusMultiplierDamage],
        total_dmg: int,
    ):
        self.random_factor = random_factor
        self.base_dmg = base_dmg
        self.applied_feasibility_boosts = applied_feasibility_boosts
        self.applied_potential_damage_boosts = applied_potential_damage_boosts
        self.feasibility = feasibility
        self.potential_damage = potential_damage
        self.llm_dmg_impact = llm_dmg_impact
        self.llm_dmg_scaling = llm_dmg_scaling
        self.llm_scaled_base_dmg = llm_scaled_base_dmg
        self.answer_speed_s = answer_speed_s
        self.n_new_words_in_action = n_new_words_in_action
        self.n_overused_words_in_action = n_overused_words_in_action
        self.applied_bonus_multiplier_damages = applied_bonus_multiplier_damages
        self.total_dmg = total_dmg

    def _applied_feasibility_boosts_string(self):
        if not self.applied_feasibility_boosts:
            return ""

        items_string = "\n  - ".join(
            [
                f"{boost.item_name} {boost.boost_name}: feasibility {boost.base_scaling} -> {boost.boosted_scaling}"
                for boost in self.applied_feasibility_boosts
            ]
        )
        return f"Item feasibility boosts:\n  - {items_string}"

    def _applied_potential_damage_boosts_string(self):
        if not self.applied_potential_damage_boosts:
            return ""

        items_string = "\n  - ".join(
            [
                f"{boost.item_name} {boost.boost_name}: potential damage {boost.base_scaling} -> {boost.boosted_scaling}"
                for boost in self.applied_potential_damage_boosts
            ]
        )
        return f"Item potential damage boosts:\n  - {items_string}"

    def _applied_bonus_multiplier_damages_string(self):
        if not self.applied_bonus_multiplier_damages:
            return ""

        items_string = "\n  - ".join(
            [
                f"📦 {boost.bonus_multiplier.item_name} ({boost.bonus_multiplier.boost_name})\n"
                f"    • Triggered by: {boost.bonus_multiplier.proc_reason.proc_condition.value} = {boost.bonus_multiplier.proc_reason.condition_value}\n"
                f"    • Effect: x{boost.bonus_multiplier.multiplier} multiplier\n"
                f"    • Damage: {'+' if boost.damage_impact >= 0 else '-'}{abs(boost.damage_impact)}"
                for boost in self.applied_bonus_multiplier_damages
            ]
        )
        return f"🎯 Item Effects:\n  - {items_string}"

    def to_string_debug(self, is_hero_turn: bool):
        base_string = "Damage calculation debug"
        base_string += f"\n  - base damage: {self.base_dmg}"
        base_string += f"\n  - feasibility: {self.feasibility}"
        base_string += f"\n  - potential damage: {self.potential_damage}"
        base_string += f"\n  - llm dmg impact: {self.llm_dmg_impact}"
        base_string += f"\n  - llm dmg scaling: {self.llm_dmg_scaling}"
        base_string += f"\n  - llm scaled base dmg: {self.llm_scaled_base_dmg}"
        if is_hero_turn:
            base_string += f"\n  - answer speed s: {self.answer_speed_s}"
            base_string += f"\n  - n new words in action: {self.n_new_words_in_action}"
            base_string += (
                f"\n  - n overused words in action: {self.n_overused_words_in_action}"
            )
        if is_hero_turn:
            if self._applied_feasibility_boosts_string():
                base_string += f"\n\n{self._applied_feasibility_boosts_string()}"
            else:
                base_string += "\n\nNo feasibility boosts applied"
            if self._applied_potential_damage_boosts_string():
                base_string += f"\n\n{self._applied_potential_damage_boosts_string()}"
            else:
                base_string += "\n\nNo potential damage boosts applied"
            if self._applied_bonus_multiplier_damages_string():
                base_string += f"\n\n{self._applied_bonus_multiplier_damages_string()}"
            else:
                base_string += "\n\nNo bonus multipliers applied"

        base_string += f"\n\n💥 Total damage: {self.total_dmg}"
        return base_string

    def to_string(self, is_hero_turn: bool):
        base_string = f"💥 Total damage: {self.total_dmg}"
        base_string += f"\n  - feasibility: {self.feasibility}"
        base_string += f"\n  - potential damage: {self.potential_damage}"
        if is_hero_turn:
            if self._applied_feasibility_boosts_string():
                base_string += f"\n  - {self._applied_feasibility_boosts_string()}"
            if self._applied_potential_damage_boosts_string():
                base_string += f"\n  - {self._applied_potential_damage_boosts_string()}"
            base_string += f"\n  - answer speed s: {self.answer_speed_s}"
            base_string += f"\n  - n new words in action: {self.n_new_words_in_action}"
            base_string += (
                f"\n  - n overused words in action: {self.n_overused_words_in_action}"
            )
            if self._applied_bonus_multiplier_damages_string():
                base_string += (
                    f"\n  - {self._applied_bonus_multiplier_damages_string()}"
                )

        return base_string


class DamageCalculator:
    def __init__(
        self,
        game_config: GameConfig,
    ):
        self.ad_diff_scaling = game_config.damage_calculation.ad_diff_scaling
        self.ad_parity_dmg = game_config.damage_calculation.ad_parity_dmg
        self.random_factor_max = game_config.damage_calculation.random_factor_max
        self.random_factor_min = game_config.damage_calculation.random_factor_min
        self.llm_dmg_impact = game_config.damage_calculation.llm_dmg_impact

    def _boost_feasibility(
        self, base_feasibility: float, items: List[Item]
    ) -> Tuple[float, List[LLMScalingBoost]]:
        applied_feasibility_boosts: List[LLMScalingBoost] = []
        boosted_feasibility = base_feasibility
        for item in items:
            feasibility_boost = item.boost_feasibility(boosted_feasibility)
            if feasibility_boost.is_applied:
                applied_feasibility_boosts.append(feasibility_boost)
                boosted_feasibility = feasibility_boost.boosted_scaling
        return boosted_feasibility, applied_feasibility_boosts

    def _boost_potential_damage(
        self, base_potential_damage: float, items: List[Item]
    ) -> Tuple[float, List[LLMScalingBoost]]:
        applied_potential_damage_boosts: List[LLMScalingBoost] = []
        boosted_potential_damage = base_potential_damage
        for item in items:
            potential_damage_boost = item.boost_potential_damage(
                boosted_potential_damage
            )
            if potential_damage_boost.is_applied:
                applied_potential_damage_boosts.append(potential_damage_boost)
                boosted_potential_damage = potential_damage_boost.boosted_scaling
        return boosted_potential_damage, applied_potential_damage_boosts

    def _proc_bonus_multipliers(
        self,
        n_new_words_in_action: int,
        n_overused_words_in_action: int,
        answer_speed_s: float,
        items: List[Item],
    ) -> List[BonusMultiplier]:
        applied_bonus_multipliers: List[BonusMultiplier] = []
        for item in items:
            bonus_multipliers = item.get_bonus_multipliers(
                n_new_words_in_action=n_new_words_in_action,
                n_overused_words_in_action=n_overused_words_in_action,
                answer_speed_s=answer_speed_s,
            )
            for bonus_multiplier in bonus_multipliers:
                if bonus_multiplier.is_procced:
                    applied_bonus_multipliers.append(bonus_multiplier)
        return applied_bonus_multipliers

    def _apply_procced_bonus_multipliers(
        self,
        llm_scaled_base_dmg: float,
        applied_bonus_multipliers: List[BonusMultiplier],
    ) -> Tuple[int, List[BonusMultiplierDamage]]:
        applied_bonus_multiplier_damages: List[BonusMultiplierDamage] = []
        total_bonus_damage = 0
        for bonus_multiplier in applied_bonus_multipliers:
            raw_bonus_damage = llm_scaled_base_dmg * bonus_multiplier.multiplier
            if raw_bonus_damage < 0:
                scaled_bonus_damage = floor(raw_bonus_damage)
            else:
                scaled_bonus_damage = ceil(raw_bonus_damage)
            applied_bonus_multiplier_damages.append(
                BonusMultiplierDamage(
                    bonus_multiplier=bonus_multiplier,
                    damage_impact=scaled_bonus_damage,
                )
            )
            total_bonus_damage += scaled_bonus_damage
        return total_bonus_damage, applied_bonus_multiplier_damages

    def calculate_damage(
        self,
        attack: float,
        defense: float,
        feasibility: float,
        potential_damage: float,
        n_new_words_in_action: int,
        n_overused_words_in_action: int,
        answer_speed_s: float,
        equiped_items: List[Item],
    ) -> DamageCalculationResult:
        # base dmg depends purely on stats and random factor
        random_factor = random.uniform(self.random_factor_min, self.random_factor_max)
        base_dmg = max(
            1,
            (self.ad_parity_dmg + (self.ad_diff_scaling * (attack - defense)))
            * random_factor,
        )

        # boost feasibility
        boosted_feasibility, applied_feasibility_boosts = self._boost_feasibility(
            feasibility, equiped_items
        )

        # boost potential damage
        boosted_potential_damage, applied_potential_damage_boosts = (
            self._boost_potential_damage(potential_damage, equiped_items)
        )

        # llm dmg depends on feasibility and potential damage
        llm_dmg_scaling = (
            self.llm_dmg_impact * boosted_feasibility * boosted_potential_damage
        )
        llm_scaled_base_dmg = ceil(base_dmg * llm_dmg_scaling)

        # proc items that have bonus multipliers
        procced_bonus_multipliers = self._proc_bonus_multipliers(
            n_new_words_in_action,
            n_overused_words_in_action,
            answer_speed_s,
            equiped_items,
        )

        # apply bonus multipliers
        total_bonus_damage, applied_bonus_multiplier_damages = (
            self._apply_procced_bonus_multipliers(
                llm_scaled_base_dmg, procced_bonus_multipliers
            )
        )

        # calculate total damage
        total_dmg = llm_scaled_base_dmg + total_bonus_damage
        if total_dmg < 0:
            total_dmg = 0

        return DamageCalculationResult(
            random_factor=random_factor,
            base_dmg=base_dmg,
            applied_feasibility_boosts=applied_feasibility_boosts,
            applied_potential_damage_boosts=applied_potential_damage_boosts,
            feasibility=boosted_feasibility,
            potential_damage=boosted_potential_damage,
            llm_dmg_impact=self.llm_dmg_impact,
            llm_dmg_scaling=llm_dmg_scaling,
            llm_scaled_base_dmg=llm_scaled_base_dmg,
            answer_speed_s=answer_speed_s,
            n_new_words_in_action=n_new_words_in_action,
            n_overused_words_in_action=n_overused_words_in_action,
            applied_bonus_multiplier_damages=applied_bonus_multiplier_damages,
            total_dmg=total_dmg,
        )
