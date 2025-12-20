from __future__ import annotations
import pygame
from llm_rpg.game.game_config import GameConfig
from llm_rpg.scenes.factory import SceneFactory
from llm_rpg.systems.hero.hero import Hero
from llm_rpg.llm.llm import LLM

from typing import TYPE_CHECKING
from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.utils.theme import Theme
from llm_rpg.systems.generation.enemy_generator import EnemyGenerator

if TYPE_CHECKING:
    from llm_rpg.scenes.scene import Scene


class Game:
    DESIGN_WIDTH = 320
    DESIGN_HEIGHT = 240

    def __init__(self, config: GameConfig):
        self.config = config
        self.action_judge = config.action_judge
        self.action_narrator = config.action_narrator
        self.enemy_action_generator = config.enemy_action_generator
        self.is_running = True
        self.hero = Hero(
            name="",
            class_name="",
            description="",
            level=1,
            base_stats=self.config.hero_base_stats,
            max_items=self.config.hero_max_items,
        )
        self.enemy_generator = EnemyGenerator(
            llm=self.config.enemy_generation_llm,
            prompt=self.config.enemy_generation_prompt,
            enemy_action_generator=self.enemy_action_generator,
            base_stats=self.config.base_enemy_stats,
            debug=self.config.debug_mode,
        )
        # pygame initialization early so surfaces can convert properly
        pygame.init()
        pygame.display.set_caption("LLM RPG")
        self.theme = Theme()
        self.clock = pygame.time.Clock()

        # display setup
        self.design_surface = pygame.Surface((self.DESIGN_WIDTH, self.DESIGN_HEIGHT))
        if config.display_fullscreen:
            self._setup_fullscreen()
        else:
            self._setup_windowed()
        # scene setup
        self.scene_factory = SceneFactory(self)
        self.current_scene: Scene = self.scene_factory.get_initial_scene()
        self.battles_won = 0
        self.llms = self._get_llms()

    def _setup_fullscreen(self):
        display_info = pygame.display.Info()
        scale_x = display_info.current_w // self.DESIGN_WIDTH
        scale_y = display_info.current_h // self.DESIGN_HEIGHT
        scale = min(scale_x, scale_y, 6)

        window_width = self.DESIGN_WIDTH * scale
        window_height = self.DESIGN_HEIGHT * scale
        self.screen = pygame.display.set_mode(
            (window_width, window_height), pygame.FULLSCREEN
        )

    def _setup_windowed(self):
        window_width = self.DESIGN_WIDTH * self.config.display_windowed_scale
        window_height = self.DESIGN_HEIGHT * self.config.display_windowed_scale
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

    def _get_llms(self) -> list[LLM]:
        llms = []
        for provider in [
            self.action_judge,
            self.action_narrator,
            self.enemy_action_generator,
            self.enemy_generator,
        ]:
            llm = getattr(provider, "llm", None)
            if llm is not None:
                llms.append(llm)
        return llms

    def _get_total_llm_cost(self) -> float:
        return sum(llm.llm_cost_tracker.total_cost for llm in self.llms)

    def run(self):
        while self.is_running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                else:
                    self.current_scene.handle_input(event)
            self.current_scene.update(dt)
            self.current_scene.render(self.design_surface)

            scaled = pygame.transform.scale(self.design_surface, self.screen.get_size())
            self.screen.blit(scaled, (0, 0))
            pygame.display.flip()

        print(f"Total llm cost $: {self._get_total_llm_cost()}")
