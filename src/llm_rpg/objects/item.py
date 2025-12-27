from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import List


# in the future we might limit users to 1 of each item type
class ItemType(Enum):
    WEAPON = "weapon"
    BOOTS = "boots"
    HELMET = "helmet"
    ARMOR = "armor"
    ACCESSORY = "accessory"


class Rarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    SECRET = "secret"


class LLMScalingBoostType(Enum):
    FEASIBILITY = "feasibility"
    POTENTIAL_DAMAGE = "potential_damage"


@dataclass
class LLMScalingBoost:
    item_name: str
    boost_name: str
    llm_scaling_boost_type: LLMScalingBoostType
    base_scaling: float
    boosted_scaling: float
    is_applied: bool


class ProcCondition(Enum):
    N_NEW_WORDS_IN_ACTION = "new words in action"
    N_OVERUSED_WORDS_IN_ACTION = "overused words in action"
    ANSWER_SPEED_S = "answer speed (seconds)"


@dataclass
class ProcReason:
    proc_condition: ProcCondition
    condition_value: float


@dataclass
class BonusMultiplier:
    item_name: str
    boost_name: str
    multiplier: float
    is_procced: bool
    proc_reason: ProcReason


class Item(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        item_type: ItemType,
        rarity: Rarity,
    ):
        self.name = name
        self.description = description
        self.item_type = item_type
        self.rarity = rarity

    def boost_attack(self, current_attack: int) -> int:
        return current_attack

    def boost_defense(self, current_defense: int) -> int:
        return current_defense

    def boost_focus(self, current_focus: int) -> int:
        return current_focus

    def boost_max_hp(self, current_max_hp: int) -> int:
        return current_max_hp

    def boost_feasibility(self, current_feasibility: float) -> LLMScalingBoost:
        return LLMScalingBoost(
            item_name=self.name,
            boost_name="none",
            llm_scaling_boost_type=LLMScalingBoostType.FEASIBILITY,
            base_scaling=current_feasibility,
            boosted_scaling=current_feasibility,
            is_applied=False,
        )

    def boost_potential_damage(
        self, current_potential_damage: float
    ) -> LLMScalingBoost:
        return LLMScalingBoost(
            item_name=self.name,
            boost_name="none",
            llm_scaling_boost_type=LLMScalingBoostType.POTENTIAL_DAMAGE,
            base_scaling=current_potential_damage,
            boosted_scaling=current_potential_damage,
            is_applied=False,
        )

    def get_bonus_multipliers(
        self,
        # TODO: needs access to more information for more creative bonusses which
        # target specific keywords etc.
        n_new_words_in_action: int,
        n_overused_words_in_action: int,
        answer_speed_s: float,
    ) -> List[BonusMultiplier]:
        return []

    def rarity_to_string(self) -> str:
        return self.rarity.value


# ITEMS

# STARTING ITEMS


class AttackerStartingItem(Item):
    def __init__(self):
        super().__init__(
            name="Baseball Bat",
            description="A simple baseball bat. Increases attack by 5.",
            item_type=ItemType.WEAPON,
            rarity=Rarity.COMMON,
        )

    def boost_attack(self, current_attack: int) -> int:
        return current_attack + 5


class DefenderStartingItem(Item):
    def __init__(self):
        super().__init__(
            name="Turtle Shell",
            description="A turtle shell. Increases defense by 5.",
            item_type=ItemType.ARMOR,
            rarity=Rarity.COMMON,
        )

    def boost_defense(self, current_defense: int) -> int:
        return current_defense + 5


class FocusStartingItem(Item):
    def __init__(self):
        super().__init__(
            name="Chewed Up Pen",
            description="A chewed up pen. Increases focus by 5.",
            item_type=ItemType.ACCESSORY,
            rarity=Rarity.COMMON,
        )

    def boost_focus(self, current_focus: int) -> int:
        return current_focus + 5


# COMMON ITEMS


# BASE STAT BOOSTS
class LaserPistol(Item):
    def __init__(self):
        super().__init__(
            name="Laser Pistol",
            description="A laser pistol. Increases attack by 10.",
            item_type=ItemType.WEAPON,
            rarity=Rarity.COMMON,
        )

    def boost_attack(self, current_attack: int) -> int:
        return current_attack + 10


class TurtleShell(Item):
    def __init__(self):
        super().__init__(
            name="Riot Shield",
            description="A riot shield. Increases defense by 10.",
            item_type=ItemType.ARMOR,
            rarity=Rarity.COMMON,
        )

    def boost_defense(self, current_defense: int) -> int:
        return current_defense + 10


class AdderallBox(Item):
    def __init__(self):
        super().__init__(
            name="Adderall Box",
            description="Box of pills that enhances mental clarity. Increases focus by 10.",
            item_type=ItemType.ACCESSORY,
            rarity=Rarity.COMMON,
        )

    def boost_focus(self, current_focus: int) -> int:
        return current_focus + 10


class HeartTransplant(Item):
    def __init__(self):
        super().__init__(
            name="Heart Transplant",
            description="A heart transplant. Increases max hp by 10.",
            item_type=ItemType.ACCESSORY,
            rarity=Rarity.COMMON,
        )

    def boost_max_hp(self, current_max_hp: int) -> int:
        return current_max_hp + 10


class AdrenalinePump(Item):
    def __init__(self):
        super().__init__(
            name="Adrenaline Pump",
            description="A pump that increases adrenaline. Do 30% more damage when you typed your answer in faster than 10 seconds.",
            item_type=ItemType.ACCESSORY,
            rarity=Rarity.UNCOMMON,
        )

    def get_bonus_multipliers(
        self,
        n_new_words_in_action: int,
        n_overused_words_in_action: int,
        answer_speed_s: float,
    ) -> list[BonusMultiplier]:
        bonus_multipliers = []
        if answer_speed_s < 10:
            bonus_multipliers.append(
                BonusMultiplier(
                    item_name=self.name,
                    boost_name="Answer speed bonus",
                    multiplier=0.3,
                    is_procced=True,
                    proc_reason=ProcReason(
                        proc_condition=ProcCondition.ANSWER_SPEED_S,
                        condition_value=answer_speed_s,
                    ),
                )
            )
        return bonus_multipliers


# Instantiate items
ALL_ITEMS: List[Item] = [
    LaserPistol(),
    TurtleShell(),
    AdderallBox(),
    HeartTransplant(),
    AdrenalinePump(),
]
