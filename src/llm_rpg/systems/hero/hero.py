from dataclasses import dataclass
from llm_rpg.objects.character import Character, Stats
from llm_rpg.objects.character import StatTypes
from llm_rpg.objects.item import (
    Item,
)
from llm_rpg.systems.hero.inventory import Inventory


@dataclass
class ProposedHeroAction:
    action: str
    time_to_answer_seconds: float
    is_valid: bool
    invalid_reason: str = None


@dataclass
class HeroClass:
    class_name: str
    description: str
    base_stats: Stats
    starting_item: Item


class Hero(Character):
    def __init__(
        self,
        name: str,
        class_name: str,
        description: str,
        level: int,
        base_stats: Stats,
        max_items: int,
    ):
        super().__init__(
            name=name, description=description, level=level, base_stats=base_stats
        )
        self.class_name = class_name
        self.inventory = Inventory(max_items=max_items)
        self.discovered_item = False

    def dont_pick_up_item(self):
        self.discovered_item = False

    def replace_item_with_discovered_item(
        self, item_to_remove: Item, discovered_item: Item
    ):
        self.inventory.remove_item(item_to_remove)
        self.inventory.add_item(discovered_item)
        self.discovered_item = False

    def pick_up_discovered_item(self, item: Item):
        self.inventory.add_item(item)
        self.discovered_item = False

    def get_current_stats(self) -> Stats:
        base_stats = Stats(
            attack=self.base_stats.attack,
            defense=self.base_stats.defense,
            focus=self.base_stats.focus,
            max_hp=self.base_stats.max_hp,
        )
        for item in self.inventory.items:
            base_stats.attack = item.boost_attack(base_stats.attack)
            base_stats.defense = item.boost_defense(base_stats.defense)
            base_stats.focus = item.boost_focus(base_stats.focus)
            base_stats.max_hp = item.boost_max_hp(base_stats.max_hp)
        return base_stats

    def level_up(self, stat_type: StatTypes, amount: int):
        super().level_up(stat_type, amount)
        self.full_heal()

    def full_heal(self):
        self.hp = self.get_current_stats().max_hp
