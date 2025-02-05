from __future__ import annotations


from llm_rpg.scenes.main_menu.main_menu_states.main_menu_states import MainMenuStates
from llm_rpg.scenes.state import State

from typing import TYPE_CHECKING

from llm_rpg.utils.rendering import render_state_transition_header
from llm_rpg.utils.user_navigation_input import (
    UserNavigationInput,
    get_user_navigation_input,
)

if TYPE_CHECKING:
    from llm_rpg.scenes.main_menu.main_menu_scene import MainMenuScene


class MainMenuInfoState(State):
    def __init__(self, scene: MainMenuScene):
        self.scene = scene
        self.display_state_transition_header = True
        self.display_info = True
        self.last_user_navigation_input: UserNavigationInput | None = None

    def handle_input(self):
        self.last_user_navigation_input = get_user_navigation_input([1])

    def update(self):
        self.display_info = False
        self.display_state_transition_header = False
        if self.last_user_navigation_input.is_valid:
            if self.last_user_navigation_input.choice == 1:
                self.scene.change_state(MainMenuStates.NAVIGATION)

    def _render_game_info(self):
        print(
            "You choose a character class and fight against increasing difficult enemies."
        )
        print(
            "You can freely type your actions and an llm will judge the consequences."
        )
        print(
            "LLM will judge your action based on the battle situation, your character class and your items"
        )
        print("LLM will output: feasiblity of action and potential damage")
        print("Besides LLM based damage your character has following attributes:")
        print("Attack: influences damage dealt to enemies")
        print("Defense: influences damage taken from enemies")
        print("HP: how much damage you can take")
        print("Focus: How much characters you can type in each turn")
        print("")
        print("Choose an option:")
        print("[1] Back to main menu")

    def _render_invalid_choice(self):
        print("Invalid choice. Choose [1]")

    def render(self):
        if self.display_state_transition_header:
            render_state_transition_header(
                "Info",
            )
        if self.display_info:
            self._render_game_info()
        if (
            self.last_user_navigation_input
            and not self.last_user_navigation_input.is_valid
        ):
            self._render_invalid_choice()
