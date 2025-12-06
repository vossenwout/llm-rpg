from __future__ import annotations

from typing import TYPE_CHECKING


from llm_rpg.scenes.main_menu.main_menu_states.main_menu_info_state import (
    MainMenuInfoState,
)
from llm_rpg.scenes.main_menu.main_menu_states.main_menu_navigation_state import (
    MainMenuNavigationState,
)
from llm_rpg.scenes.main_menu.main_menu_states.main_menu_states import MainMenuStates
from llm_rpg.scenes.scene import Scene


if TYPE_CHECKING:
    from llm_rpg.game.game import Game


class MainMenuScene(Scene):
    def __init__(self, game: Game):
        super().__init__(game=game)
        self.current_state = MainMenuNavigationState(self)

    def change_state(self, new_state: MainMenuStates):
        if new_state == MainMenuStates.NAVIGATION:
            self.current_state = MainMenuNavigationState(self)
        elif new_state == MainMenuStates.INFO:
            self.current_state = MainMenuInfoState(self)
