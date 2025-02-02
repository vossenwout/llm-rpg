from __future__ import annotations


from typing import TYPE_CHECKING


from llm_rpg.scenes.scene import SceneTypes
from llm_rpg.scenes.state import State

if TYPE_CHECKING:
    from llm_rpg.scenes.resting_hub.resting_hub_scene import RestingHubScene


class RestingHubViewCharacterState(State):
    def __init__(self, resting_hub_scene: RestingHubScene):
        self.resting_hub_scene = resting_hub_scene

    def handle_input(self):
        pass

    def update(self):
        self.resting_hub_scene.game.change_scene(SceneTypes.RESTING_HUB)

    def _render_character(self):
        print("")
        print(f"Name: {self.resting_hub_scene.game.hero.name}")
        print(f"Level: {self.resting_hub_scene.game.hero.description}")
        print(f"Attack: {self.resting_hub_scene.game.hero.get_current_stats().attack}")
        print(
            f"Defense: {self.resting_hub_scene.game.hero.get_current_stats().defense}"
        )
        print(f"Focus: {self.resting_hub_scene.game.hero.get_current_stats().focus}")
        print(f"HP: {self.resting_hub_scene.game.hero.get_current_stats().max_hp}")

    def render(self):
        self._render_character()
