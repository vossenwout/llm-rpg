from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict
from llm_rpg.systems.battle.enemy import Enemy, EnemyArchetypes

if TYPE_CHECKING:
    from llm_rpg.game.game import Game


@dataclass
class BaseEnemyInfo:
    name: str
    description: str
    archetype: EnemyArchetypes


devil_dog = BaseEnemyInfo(
    name="Devil Dog",
    description="The pet of Lucifer, seems hungry.",
    archetype=EnemyArchetypes.ATTACKER,
)

golden_trophy = BaseEnemyInfo(
    name="Golden Trophy",
    description="Suddenly became alive after being thrown in the trash.",
    archetype=EnemyArchetypes.TANK,
)

hippy = BaseEnemyInfo(
    name="Hippy",
    description="Annoyed after the cops took his weed.",
    archetype=EnemyArchetypes.TANK,
)

mushroom_head = BaseEnemyInfo(
    name="Mushroom Head",
    description="Somehow became conscious.",
    archetype=EnemyArchetypes.TANK,
)

pile_of_goo = BaseEnemyInfo(
    name="Pile of Goo",
    description="Seems cute, but very poisonous.",
    archetype=EnemyArchetypes.TANK,
)

rat = BaseEnemyInfo(
    name="Rat",
    description="Found in the trash, with sharp teeth and a quick bite",
    archetype=EnemyArchetypes.ATTACKER,
)

robert = BaseEnemyInfo(
    name="Robert",
    description="Robot that can shoot lasers from his eyes.",
    archetype=EnemyArchetypes.ATTACKER,
)

taxi = BaseEnemyInfo(
    name="Taxi",
    description="From the streets of New York, known for his aggresive driving style.",
    archetype=EnemyArchetypes.TANK,
)

tree = BaseEnemyInfo(
    name="Tree",
    description="Grew an appetite for human flesh.",
    archetype=EnemyArchetypes.TANK,
)


battles_won_to_enemies_mapping: Dict[int, BaseEnemyInfo] = {
    0: devil_dog,
    1: hippy,
    2: taxi,
    3: golden_trophy,
    4: tree,
    5: pile_of_goo,
    6: mushroom_head,
    7: robert,
    8: devil_dog,
}


def generate_enemy(game: Game) -> Enemy:
    battles_won = game.battles_won
    enemy_info = battles_won_to_enemies_mapping[battles_won]
    return Enemy(
        name=enemy_info.name,
        description=enemy_info.description,
        level=1,
        base_stats=game.config.base_enemy_stats,
        llm=game.llm,
        enemy_next_action_prompt=game.config.enemy_next_action_prompt,
        archetype=enemy_info.archetype,
    )
