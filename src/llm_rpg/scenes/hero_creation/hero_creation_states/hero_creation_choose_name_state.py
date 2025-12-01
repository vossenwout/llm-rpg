from __future__ import annotations

import pygame
from llm_rpg.scenes.hero_creation.hero_creation_states.hero_creation_states import (
    HeroCreationStates,
)
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import draw_panel, draw_blinking_cursor

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
                if event.unicode.isprintable() and len(self.current_name) < 15:
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

        title_text = self.scene.game.theme.fonts["title"].render(
            "Character Creation: Name", True, self.scene.game.theme.colors["primary"]
        )
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, spacing(1.5)))
        screen.blit(title_text, title_rect)

        panel_width = screen.get_width() - spacing(2)
        panel_height = spacing(6)
        panel_rect = pygame.Rect(
            spacing(1),
            spacing(3),
            panel_width,
            panel_height,
        )
        draw_panel(screen, panel_rect, self.scene.game.theme)

        prompt_text = self.scene.game.theme.fonts["medium"].render(
            "Enter a name for your hero (max 10 characters):",
            True,
            self.scene.game.theme.colors["text"],
        )
        prompt_rect = prompt_text.get_rect(
            center=(screen.get_width() // 2, panel_rect.top + spacing(1))
        )
        screen.blit(prompt_text, prompt_rect)

        input_box_width = screen.get_width() - spacing(5)
        input_box_height = spacing(2.5)
        input_box_x = spacing(2)
        input_box_y = panel_rect.top + spacing(2)
        input_box_rect = pygame.Rect(
            input_box_x, input_box_y, input_box_width, input_box_height
        )
        draw_panel(screen, input_box_rect, self.scene.game.theme)

        name_text = self.scene.game.theme.fonts["medium"].render(
            self.current_name,
            True,
            self.scene.game.theme.colors["text_selected"],
        )
        name_rect = name_text.get_rect(
            center=(screen.get_width() // 2, input_box_y + 25)
        )
        screen.blit(name_text, name_rect)

        cursor_x = name_rect.right + 6
        cursor_y = name_rect.top
        draw_blinking_cursor(
            screen,
            cursor_x,
            cursor_y,
            name_rect.height,
            self.scene.game.theme,
            pygame.time.get_ticks(),
        )

        if self.error_message:
            error_text = self.scene.game.theme.fonts["small"].render(
                self.error_message,
                True,
                (255, 50, 50),
            )
            error_rect = error_text.get_rect(
                center=(screen.get_width() // 2, panel_rect.bottom - spacing(0.5))
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
