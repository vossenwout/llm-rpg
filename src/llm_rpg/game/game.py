from __future__ import annotations
import pygame
from llm_rpg.game.game_config import GameConfig
from llm_rpg.scenes.factory import SceneFactory
from llm_rpg.systems.hero.hero import Hero

from typing import TYPE_CHECKING
from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.utils.theme import Theme

if TYPE_CHECKING:
    from llm_rpg.scenes.scene import Scene


class Game:
    DESIGN_WIDTH = 480
    DESIGN_HEIGHT = 270
    MAX_SCALE = 6

    def __init__(self, config: GameConfig):
        self.config = config
        self.llm = config.llm
        self.is_running = True
        self.hero = Hero(
            name="",
            class_name="",
            description="",
            level=1,
            base_stats=self.config.hero_base_stats,
            max_items=self.config.hero_max_items,
        )
        pygame.init()
        pygame.display.set_caption("LLM RPG")

        if config.display_fullscreen:
            self._setup_fullscreen()
        else:
            self._setup_windowed()

        self.theme = Theme(scale=self.scale)
        self.clock = pygame.time.Clock()

        self.scene_factory = SceneFactory(self)
        self.current_scene: Scene = self.scene_factory.get_initial_scene()
        self.battles_won = 0

    def _setup_fullscreen(self):
        display_info = pygame.display.Info()
        scale_x = display_info.current_w // self.DESIGN_WIDTH
        scale_y = display_info.current_h // self.DESIGN_HEIGHT
        self.scale = min(scale_x, scale_y, self.MAX_SCALE)

        window_width = self.DESIGN_WIDTH * self.scale
        window_height = self.DESIGN_HEIGHT * self.scale
        self.screen = pygame.display.set_mode(
            (window_width, window_height), pygame.FULLSCREEN
        )

    def _setup_windowed(self):
        self.scale = self.config.display_windowed_scale
        window_width = self.DESIGN_WIDTH * self.scale
        window_height = self.DESIGN_HEIGHT * self.scale
        self.screen = pygame.display.set_mode((window_width, window_height))

    def change_scene(self, scene_type: SceneTypes):
        if scene_type == SceneTypes.BATTLE:
            self.current_scene = self.scene_factory.get_battle_scene()
        elif scene_type == SceneTypes.RESTING_HUB:
            self.current_scene = self.scene_factory.get_resting_hub_scene()
        elif scene_type == SceneTypes.HERO_CREATION:
            self.current_scene = self.scene_factory.get_hero_creation_scene()
        elif scene_type == SceneTypes.GAME_OVER:
            self.current_scene = self.scene_factory.get_game_over_scene()
        elif scene_type == SceneTypes.MAIN_MENU:
            self.current_scene = self.scene_factory.get_main_menu_scene()
        else:
            raise ValueError(f"Tried to change to invalid scene: {scene_type}")

    def run(self):
        while self.is_running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                else:
                    self.current_scene.handle_input(event)
            self.current_scene.update(dt)
            self.current_scene.render(self.screen)
            pygame.display.flip()

        print(f"Total llm cost $: {self.llm.llm_cost_tracker.total_cost}")
