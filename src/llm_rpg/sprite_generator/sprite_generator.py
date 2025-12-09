from abc import ABC, abstractmethod

import pygame


class SpriteGenerator(ABC):
    @abstractmethod
    def generate_sprite(self, prompt: str) -> pygame.Surface:
        pass


class DummySpriteGenerator(SpriteGenerator):
    def generate_sprite(self, prompt: str) -> pygame.Surface:
        prompt = prompt.lower()
        if prompt == "devil dog":
            return pygame.Surface((32, 32))
        elif prompt == "golden trophy":
            return pygame.Surface((32, 32))
        elif prompt == "hippy":
            return pygame.Surface((32, 32))
        elif prompt == "mushroom head":
            return pygame.Surface((32, 32))
        elif prompt == "pile of goo":
            return pygame.Surface((32, 32))
        elif prompt == "rat":
            return pygame.Surface((32, 32))
        elif prompt == "robert":
            return pygame.Surface((32, 32))
        elif prompt == "taxi":
            return pygame.Surface((32, 32))
        elif prompt == "tree":
            return pygame.Surface((32, 32))
        else:
            raise ValueError(f"Unknown dummy sprite: {prompt}")
