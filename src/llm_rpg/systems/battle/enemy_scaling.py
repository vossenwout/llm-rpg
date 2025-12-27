from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass
from math import floor
import random

from llm_rpg.objects.character import StatTypes, Stats
from llm_rpg.systems.battle.enemy import Enemy, EnemyArchetypes

if TYPE_CHECKING:
    from llm_rpg.game.game_config import GameConfig


@dataclass
class LevelScaling:
    exp_growth_rate: float
    linear_growth_rate: float
    linear_scaling_factor: float


@dataclass
class LevelingAttributeProbs:
    attack: float
    defense: float
    max_hp: float


@dataclass
class EnemyArchetypesLevelingAttributeProbs:
    attacker: LevelingAttributeProbs
    defender: LevelingAttributeProbs
    tank: LevelingAttributeProbs


@dataclass
class BaseEnemyStats:
    attack: float
    defense: float
    max_hp: float


def _get_enemy_scaled_level(
    battles_won: int,
    linear_growth_rate: float,
    linear_scaling_factor: float,
    exp_growth_rate: float,
    exponential_scaling_factor: float,
) -> int:
    # we already want to level up the enemy for the first battle to create variance
    progress = battles_won + 1

    linear_scaled_stat = linear_growth_rate * progress
    exponential_scaled_stat = exp_growth_rate**progress

    return max(
        1,
        floor(
            linear_scaled_stat * linear_scaling_factor
            + exponential_scaled_stat * exponential_scaling_factor
        ),
    )


def _parse_leveling_attribute_probs(
    leveling_attribute_probs: LevelingAttributeProbs,
) -> dict[StatTypes, float]:
    return {
        StatTypes.ATTACK: leveling_attribute_probs.attack,
        StatTypes.DEFENSE: leveling_attribute_probs.defense,
        StatTypes.MAX_HP: leveling_attribute_probs.max_hp,
    }


def _get_leveling_attribute_probs(
    archetype: EnemyArchetypes, game_config: GameConfig
) -> dict[StatTypes, float]:
    if archetype == EnemyArchetypes.ATTACKER:
        return _parse_leveling_attribute_probs(
            game_config.enemy_leveling_stats_probs.attacker
        )
    elif archetype == EnemyArchetypes.DEFENDER:
        return _parse_leveling_attribute_probs(
            game_config.enemy_leveling_stats_probs.defender
        )
    elif archetype == EnemyArchetypes.TANK:
        return _parse_leveling_attribute_probs(
            game_config.enemy_leveling_stats_probs.tank
        )
    else:
        raise ValueError(f"Invalid enemy archetype: {archetype}")


def scale_enemy(
    enemy: Enemy, battles_won: int, game_config: GameConfig, debug: bool = False
):
    enemy_level = _get_enemy_scaled_level(
        battles_won=battles_won,
        exp_growth_rate=game_config.enemy_level_scaling.exp_growth_rate,
        linear_growth_rate=game_config.enemy_level_scaling.linear_growth_rate,
        linear_scaling_factor=game_config.enemy_level_scaling.linear_scaling_factor,
        exponential_scaling_factor=1
        - game_config.enemy_level_scaling.linear_scaling_factor,
    )

    leveling_attribute_probs = _get_leveling_attribute_probs(
        archetype=enemy.archetype, game_config=game_config
    )

    for _ in range(enemy_level):
        stat_type = random.choices(
            list(leveling_attribute_probs.keys()),
            list(leveling_attribute_probs.values()),
        )[0]
        enemy.level_up(
            stat_type=stat_type, amount=game_config.enemy_stats_level_up_amount
        )

    if debug:
        _debug_log(
            "Enemy scaled",
            [
                f"name: {enemy.name}",
                f"archetype: {enemy.archetype.value}",
                f"battles won: {battles_won}",
                f"level: {enemy.level}",
                f"stats: {_format_stats(enemy.base_stats)}",
            ],
        )


def _format_stats(stats: Stats) -> str:
    return (
        f"ATK {stats.attack} | DEF {stats.defense} | "
        f"FOC {stats.focus} | HP {stats.max_hp}"
    )


def _debug_log(title: str, lines: list[str]) -> None:
    print(f"\n[DEBUG] {title}")
    for line in lines:
        print(f"  {line}")
