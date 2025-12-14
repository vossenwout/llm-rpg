from __future__ import annotations
import pygame
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class State(ABC):
    @abstractmethod
    def handle_input(self, event: pygame.event.Event):
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface):
        pass
