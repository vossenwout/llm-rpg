from __future__ import annotations
from typing import TYPE_CHECKING

from llm_rpg.scenes.battle.battle_scene import BattleScene
from llm_rpg.scenes.game_over.game_over_scene import GameOverScene
from llm_rpg.scenes.hero_creation.hero_creation_scene import HeroCreationScene
from llm_rpg.scenes.main_menu.main_menu_scene import MainMenuScene
from llm_rpg.scenes.resting_hub.resting_hub_scene import RestingHubScene
from llm_rpg.scenes.scene import Scene

if TYPE_CHECKING:
    from llm_rpg.game.game import Game


class SceneFactory:
    def __init__(self, game: Game):
        self.game = game

    def get_initial_scene(self) -> Scene:
        return self.get_main_menu_scene()

    def get_battle_scene(self) -> BattleScene:
        return BattleScene(game=self.game)

    def get_resting_hub_scene(self) -> RestingHubScene:
        return RestingHubScene(game=self.game)

    def get_hero_creation_scene(self) -> HeroCreationScene:
        return HeroCreationScene(game=self.game)

    def get_game_over_scene(self) -> GameOverScene:
        return GameOverScene(game=self.game)

    def get_main_menu_scene(self) -> MainMenuScene:
        return MainMenuScene(game=self.game)
