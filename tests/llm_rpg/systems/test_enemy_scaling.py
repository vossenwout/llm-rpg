import random

from llm_rpg.objects.character import Stats
from llm_rpg.systems.battle.enemy import Enemy, EnemyArchetypes
from llm_rpg.systems.battle.enemy_scaling import (
    scale_enemy,
    LevelScaling,
    EnemyArchetypesLevelingAttributeProbs,
    LevelingAttributeProbs,
)


class _Config:
    def __init__(self):
        self.enemy_level_scaling = LevelScaling(
            exp_growth_rate=1.0,
            linear_growth_rate=1.0,
            linear_scaling_factor=1.0,
        )
        self.enemy_leveling_stats_probs = EnemyArchetypesLevelingAttributeProbs(
            attacker=LevelingAttributeProbs(attack=1.0, defense=0.0, max_hp=0.0),
            defender=LevelingAttributeProbs(attack=0.0, defense=1.0, max_hp=0.0),
            tank=LevelingAttributeProbs(attack=0.0, defense=0.0, max_hp=1.0),
        )
        self.enemy_stats_level_up_amount = 5


class _EnemyActionGeneratorStub:
    def generate_next_action(self, enemy, hero, battle_log) -> str:
        return ""


def test_scale_enemy_levels_and_applies_stat_growth(monkeypatch):
    cfg = _Config()
    enemy = Enemy(
        name="Test",
        description="",
        level=1,
        base_stats=Stats(attack=2, defense=2, focus=0, max_hp=5),
        archetype=EnemyArchetypes.ATTACKER,
        enemy_action_generator=_EnemyActionGeneratorStub(),
    )

    monkeypatch.setattr(random, "choices", lambda opts, probs: [opts[0]])

    scale_enemy(enemy, battles_won=2, game_config=cfg)

    assert enemy.level == 4
    assert enemy.base_stats.attack == 17
    assert enemy.base_stats.defense == 2
    assert enemy.base_stats.max_hp == 5
