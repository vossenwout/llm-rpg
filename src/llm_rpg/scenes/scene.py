from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

import pygame


if TYPE_CHECKING:
    from llm_rpg.game.game import Game
    from llm_rpg.scenes.state import State


class SceneTypes(Enum):
    BATTLE = "battle"
    RESTING_HUB = "resting_hub"
    HERO_CREATION = "hero_creation"
    GAME_OVER = "game_over"
    MAIN_MENU = "main_menu"


class Scene(ABC):
    def __init__(self, game: Game, current_state: State = None):
        self.game = game
        self.current_state = current_state

    @abstractmethod
    def change_state(self, new_state: Enum):
        pass

    def handle_input(self, event: pygame.event.Event):
        self.current_state.handle_input(event)

    def update(self, dt: float):
        self.current_state.update(dt)

    def render(self, screen: pygame.Surface):
        self.current_state.render(screen)
