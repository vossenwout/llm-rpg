import random

import pytest

from llm_rpg.objects.item import (
    Item,
    ItemType,
    Rarity,
    LLMScalingBoost,
    LLMScalingBoostType,
    BonusMultiplier,
    ProcReason,
    ProcCondition,
)
from llm_rpg.systems.battle.damage_calculator import (
    DamageCalculator,
    DamageCalculationConfig,
)


class _StubConfig:
    def __init__(
        self,
        *,
        ad_diff_scaling: float = 0.5,
        ad_parity_dmg: float = 1.0,
        random_factor_min: float = 1.0,
        random_factor_max: float = 1.0,
        llm_dmg_impact: int = 2,
    ):
        self.damage_calculation = DamageCalculationConfig(
            ad_diff_scaling=ad_diff_scaling,
            ad_parity_dmg=ad_parity_dmg,
            random_factor_min=random_factor_min,
            random_factor_max=random_factor_max,
            llm_dmg_impact=llm_dmg_impact,
        )


class _FeasibilityBoostItem(Item):
    def __init__(self, *, boost_to: float, name: str = "Feasibility"):
        super().__init__(
            name=name,
            description="",
            item_type=ItemType.ACCESSORY,
            rarity=Rarity.COMMON,
        )
        self.boost_to = boost_to

    def boost_feasibility(self, current_feasibility: float) -> LLMScalingBoost:
        return LLMScalingBoost(
            item_name=self.name,
            boost_name="feasibility boost",
            llm_scaling_boost_type=LLMScalingBoostType.FEASIBILITY,
            base_scaling=current_feasibility,
            boosted_scaling=self.boost_to,
            is_applied=True,
        )


class _PotentialBoostItem(Item):
    def __init__(self, *, boost_to: float, name: str = "Potential"):
        super().__init__(
            name=name,
            description="",
            item_type=ItemType.ACCESSORY,
            rarity=Rarity.COMMON,
        )
        self.boost_to = boost_to

    def boost_potential_damage(
        self, current_potential_damage: float
    ) -> LLMScalingBoost:
        return LLMScalingBoost(
            item_name=self.name,
            boost_name="potential boost",
            llm_scaling_boost_type=LLMScalingBoostType.POTENTIAL_DAMAGE,
            base_scaling=current_potential_damage,
            boosted_scaling=self.boost_to,
            is_applied=True,
        )


class _BonusMultiplierItem(Item):
    def __init__(self, multiplier: float, name: str):
        super().__init__(
            name=name,
            description="",
            item_type=ItemType.ACCESSORY,
            rarity=Rarity.UNCOMMON,
        )
        self.multiplier = multiplier

    def get_bonus_multipliers(
        self,
        n_new_words_in_action: int,
        n_overused_words_in_action: int,
        answer_speed_s: float,
    ):
        return [
            BonusMultiplier(
                item_name=self.name,
                boost_name="test bonus",
                multiplier=self.multiplier,
                is_procced=True,
                proc_reason=ProcReason(
                    proc_condition=ProcCondition.N_NEW_WORDS_IN_ACTION,
                    condition_value=n_new_words_in_action,
                ),
            )
        ]


def test_damage_calculator_base_formula_and_scaling(monkeypatch):
    cfg = _StubConfig(
        ad_diff_scaling=0.5,
        ad_parity_dmg=1.0,
        random_factor_min=1.0,
        random_factor_max=1.0,
        llm_dmg_impact=2,
    )
    calc = DamageCalculator(cfg)

    # deterministic random factor
    monkeypatch.setattr(random, "uniform", lambda a, b: 1.0)

    result = calc.calculate_damage(
        attack=10,
        defense=4,
        feasibility=1.0,
        potential_damage=1.0,
        n_new_words_in_action=0,
        n_overused_words_in_action=0,
        answer_speed_s=0.0,
        equiped_items=[],
    )

    assert result.base_dmg == pytest.approx(4.0)
    assert result.llm_dmg_scaling == pytest.approx(2.0)
    assert result.llm_scaled_base_dmg == 8  # ceil(4 * 2)
    assert result.total_dmg == 8


def test_damage_calculator_applies_item_boosts_in_order(monkeypatch):
    cfg = _StubConfig(
        ad_diff_scaling=0.0,
        ad_parity_dmg=2.0,
        random_factor_min=1.0,
        random_factor_max=1.0,
        llm_dmg_impact=1,
    )
    calc = DamageCalculator(cfg)
    monkeypatch.setattr(random, "uniform", lambda a, b: 1.0)

    items = [
        _FeasibilityBoostItem(boost_to=0.6, name="F1"),
        _FeasibilityBoostItem(boost_to=0.9, name="F2"),
        _PotentialBoostItem(boost_to=0.5, name="P1"),
        _PotentialBoostItem(boost_to=0.8, name="P2"),
    ]

    result = calc.calculate_damage(
        attack=1,
        defense=1,
        feasibility=0.5,
        potential_damage=0.4,
        n_new_words_in_action=0,
        n_overused_words_in_action=0,
        answer_speed_s=0.0,
        equiped_items=items,
    )

    # Feasibility boosts applied sequentially
    assert result.feasibility == pytest.approx(0.9)
    assert [b.item_name for b in result.applied_feasibility_boosts] == ["F1", "F2"]

    # Potential damage boosts applied sequentially
    assert result.potential_damage == pytest.approx(0.8)
    assert [b.item_name for b in result.applied_potential_damage_boosts] == [
        "P1",
        "P2",
    ]

    # llm scaling uses boosted values
    expected_scaling = cfg.damage_calculation.llm_dmg_impact * 0.9 * 0.8
    assert result.llm_dmg_scaling == pytest.approx(expected_scaling)


def test_damage_calculator_bonus_multipliers_positive_and_negative(monkeypatch):
    cfg = _StubConfig(
        ad_diff_scaling=0.0,
        ad_parity_dmg=2.0,
        random_factor_min=1.0,
        random_factor_max=1.0,
        llm_dmg_impact=1,
    )
    calc = DamageCalculator(cfg)
    monkeypatch.setattr(random, "uniform", lambda a, b: 1.0)

    items = [
        _BonusMultiplierItem(multiplier=0.5, name="Plus50%"),
        _BonusMultiplierItem(multiplier=-0.2, name="Minus20%"),
    ]

    result = calc.calculate_damage(
        attack=1,
        defense=1,
        feasibility=1.0,
        potential_damage=1.0,
        n_new_words_in_action=3,
        n_overused_words_in_action=0,
        answer_speed_s=0.0,
        equiped_items=items,
    )

    # base dmg = 2, llm scaling = 1 -> scaled base = 2
    assert result.llm_scaled_base_dmg == 2
    # bonus: ceil(2*0.5)=1, floor(2*-0.2)=-1 => net 0
    assert result.total_dmg == 2  # unchanged after net zero bonus
    assert len(result.applied_bonus_multiplier_damages) == 2


def test_damage_calculator_clamps_negative_total_to_zero(monkeypatch):
    cfg = _StubConfig(
        ad_diff_scaling=0.0,
        ad_parity_dmg=1.0,
        random_factor_min=1.0,
        random_factor_max=1.0,
        llm_dmg_impact=1,
    )
    calc = DamageCalculator(cfg)
    monkeypatch.setattr(random, "uniform", lambda a, b: 1.0)

    items = [_BonusMultiplierItem(multiplier=-2.5, name="HugePenalty")]

    result = calc.calculate_damage(
        attack=1,
        defense=1,
        feasibility=1.0,
        potential_damage=1.0,
        n_new_words_in_action=0,
        n_overused_words_in_action=0,
        answer_speed_s=0.0,
        equiped_items=items,
    )

    assert result.llm_scaled_base_dmg == 1  # base 1 * scaling 1
    assert result.total_dmg == 0  # clamped
