from __future__ import annotations
from abc import ABC, abstractmethod

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_rpg.game.game import Game


class SceneTypes(Enum):
    BATTLE = "battle"
    SHOP = "shop"
    MANAGE_CHARACTER = "manage_character"
    RESTING_HUB = "resting_hub"


class Scene(ABC):
    def __init__(self, game: Game):
        self.game = game

    @abstractmethod
    def handle_input(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass
