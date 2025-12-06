from __future__ import annotations

import pygame
from llm_rpg.scenes.hero_creation.hero_creation_states.hero_creation_states import (
    HeroCreationStates,
)
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import draw_text_panel, draw_input_panel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_rpg.scenes.hero_creation.hero_creation_scene import HeroCreationScene


class HeroCreationChooseNameState(State):
    def __init__(self, scene: HeroCreationScene):
        self.scene = scene
        self.current_name = ""
        self.error_message = ""
        self.confirm_selected = False

        self.backspace_held = False
        self.backspace_timer = 0.0
        self.backspace_initial_delay = 0.5
        self.backspace_repeat_rate = 0.05

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.confirm_selected = True
            elif event.key == pygame.K_BACKSPACE:
                self.backspace_held = True
                self.backspace_timer = 0.0
            else:
                if event.unicode.isprintable() and len(self.current_name) < 10:
                    self.current_name += event.unicode
                    self.error_message = ""
                    self.confirm_selected = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                self.backspace_held = False
                self.backspace_timer = 0.0

    def _delete_character(self):
        """Helper method to delete the last character"""
        if len(self.current_name) > 0:
            self.current_name = self.current_name[:-1]
            self.error_message = ""
            self.confirm_selected = False

    def update(self, dt: float):
        if self.backspace_held:
            if self.backspace_timer == 0.0:
                self._delete_character()

            self.backspace_timer += dt

            if self.backspace_timer >= self.backspace_initial_delay:
                time_since_delay = self.backspace_timer - self.backspace_initial_delay
                deletes_due = int(time_since_delay / self.backspace_repeat_rate)

                if deletes_due > 0:
                    self._delete_character()
                    self.backspace_timer = self.backspace_initial_delay + (
                        time_since_delay % self.backspace_repeat_rate
                    )

        if self.confirm_selected:
            if len(self.current_name) == 0:
                self.error_message = "Name cannot be empty"
                self.confirm_selected = False
            elif len(self.current_name) > 10:
                self.error_message = "Name is too long (max 10 characters)"
                self.confirm_selected = False
            else:
                self.error_message = ""
                self.scene.game.hero.name = self.current_name
                self.scene.change_state(HeroCreationStates.CHOOSE_CLASS)

    def render(self, screen: pygame.Surface):
        screen.fill(self.scene.game.theme.colors["background"])
        spacing = self.scene.game.theme.spacing

        prompt_rect = draw_text_panel(
            screen=screen,
            lines="Enter a name for your hero (max 10 characters):",
            font=self.scene.game.theme.fonts["small"],
            theme=self.scene.game.theme,
            max_width=screen.get_width() - spacing(4),
            align="left",
            auto_wrap=True,
            draw_border=True,
        )

        input_box_rect = draw_input_panel(
            screen=screen,
            current_text=self.current_name,
            font=self.scene.game.theme.fonts["small"],
            theme=self.scene.game.theme,
            y=prompt_rect.bottom + spacing(1),
            width=spacing(14),
            padding=spacing(1.5),
            template="**********",
            time_ms=pygame.time.get_ticks(),
            show_cursor=False,
            draw_border=False,
        )

        if self.error_message:
            error_text = self.scene.game.theme.fonts["small"].render(
                self.error_message,
                True,
                (255, 50, 50),
            )
            error_rect = error_text.get_rect(
                center=(screen.get_width() // 2, input_box_rect.bottom + spacing(1))
            )
            screen.blit(error_text, error_rect)

        instruction_text = self.scene.game.theme.fonts["small"].render(
            "Press ENTER to confirm",
            True,
            self.scene.game.theme.colors["text"],
        )
        instruction_rect = instruction_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - spacing(1))
        )
        screen.blit(instruction_text, instruction_rect)
