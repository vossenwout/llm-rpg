from __future__ import annotations

import pygame
from llm_rpg.scenes.hero_creation.hero_creation_states.hero_creation_states import (
    HeroCreationStates,
)
from llm_rpg.scenes.state import State

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_rpg.scenes.hero_creation.hero_creation_scene import HeroCreationScene


class HeroCreationChooseNameState(State):
    def __init__(self, scene: HeroCreationScene):
        self.scene = scene
        self.current_name = ""
        self.error_message = ""
        self.confirm_selected = False

        # Backspace hold state
        self.backspace_held = False
        self.backspace_timer = 0.0
        self.backspace_initial_delay = 0.5
        self.backspace_repeat_rate = 0.05

    def handle_input(self, event: pygame.event.Event):
        """Handle input events - only sets flags and captures input state"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.confirm_selected = True
            elif event.key == pygame.K_BACKSPACE:
                # Just set the flag - deletion logic handled in update()
                self.backspace_held = True
                self.backspace_timer = 0.0
            else:
                # Text input is kept here for immediate feedback
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
        """Update state logic - all game logic happens here"""
        # Handle backspace hold behavior
        if self.backspace_held:
            # On first frame (timer still at 0), delete immediately
            if self.backspace_timer == 0.0:
                self._delete_character()

            self.backspace_timer += dt

            # After initial delay, start repeating
            if self.backspace_timer >= self.backspace_initial_delay:
                # Calculate how many deletes should happen based on time elapsed
                time_since_delay = self.backspace_timer - self.backspace_initial_delay
                deletes_due = int(time_since_delay / self.backspace_repeat_rate)

                if deletes_due > 0:
                    self._delete_character()
                    # Reset timer but keep the "remainder" for smooth timing
                    self.backspace_timer = self.backspace_initial_delay + (
                        time_since_delay % self.backspace_repeat_rate
                    )

        # Handle name confirmation
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
        # Clear screen with a background color
        screen.fill((0, 0, 0))  # Black

        # Render title
        title_text = self.scene.game.theme.fonts["title"].render(
            "Character Creation: Name", True, self.scene.game.theme.colors["primary"]
        )
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 80))
        screen.blit(title_text, title_rect)

        # Render prompt
        prompt_text = self.scene.game.theme.fonts["medium"].render(
            "Enter a name for your hero (max 10 characters):",
            True,
            self.scene.game.theme.colors["text"],
        )
        prompt_rect = prompt_text.get_rect(center=(screen.get_width() // 2, 200))
        screen.blit(prompt_text, prompt_rect)

        # Render input box with current name
        input_box_width = 400
        input_box_height = 50
        input_box_x = (screen.get_width() - input_box_width) // 2
        input_box_y = 280

        # Draw input box background
        input_box_rect = pygame.Rect(
            input_box_x, input_box_y, input_box_width, input_box_height
        )
        pygame.draw.rect(
            screen, self.scene.game.theme.colors["text"], input_box_rect, 2
        )

        # Render current name text
        name_text = self.scene.game.theme.fonts["medium"].render(
            self.current_name + "|",  # Add cursor
            True,
            self.scene.game.theme.colors["text_selected"],
        )
        name_rect = name_text.get_rect(
            center=(screen.get_width() // 2, input_box_y + 25)
        )
        screen.blit(name_text, name_rect)

        # Render error message if any
        if self.error_message:
            error_text = self.scene.game.theme.fonts["small"].render(
                self.error_message,
                True,
                (255, 50, 50),  # Red color for errors
            )
            error_rect = error_text.get_rect(center=(screen.get_width() // 2, 360))
            screen.blit(error_text, error_rect)

        # Render instructions
        instruction_text = self.scene.game.theme.fonts["small"].render(
            "Press ENTER to confirm",
            True,
            self.scene.game.theme.colors["text"],
        )
        instruction_rect = instruction_text.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - 60)
        )
        screen.blit(instruction_text, instruction_rect)
