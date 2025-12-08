from enum import Enum
from dataclasses import dataclass


class StatTypes(Enum):
    ATTACK = "attack"
    DEFENSE = "defense"
    FOCUS = "focus"
    MAX_HP = "max HP"


@dataclass
class Stats:
    attack: int
    defense: int
    focus: int
    max_hp: int


class Character:
    def __init__(self, name: str, description: str, level: int, base_stats: Stats):
        self.name = name
        self.description = description
        self.level = level
        self.base_stats = base_stats
        self.hp = base_stats.max_hp
        self.should_level_up = False

    def inflict_damage(self, damage: int):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def is_dead(self) -> bool:
        return self.hp <= 0

    def full_heal(self):
        self.hp = self.base_stats.max_hp

    def level_up(self, stat_type: StatTypes, amount: int):
        if stat_type == StatTypes.ATTACK:
            self.base_stats.attack += amount
        elif stat_type == StatTypes.DEFENSE:
            self.base_stats.defense += amount
        elif stat_type == StatTypes.FOCUS:
            self.base_stats.focus += amount
        elif stat_type == StatTypes.MAX_HP:
            self.base_stats.max_hp += amount
            self.hp = self.base_stats.max_hp

        self.level += 1
        self.should_level_up = False
