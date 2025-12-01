from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.battle.battle_states.battle_states import BattleStates
from llm_rpg.systems.hero.hero import ProposedHeroAction
from llm_rpg.scenes.state import State
from llm_rpg.ui.battle_ui import draw_hp_bar

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene


class BattleTurnState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.input_text = ""
        self.error_message = ""
        self.submit_requested = False
        self.input_timer = 0.0

        # Backspace repeat state (mirrors hero name screen)
        self.backspace_held = False
        self.backspace_timer = 0.0
        self.backspace_initial_delay = 0.5
        self.backspace_repeat_rate = 0.05

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.submit_requested = True
            elif event.key == pygame.K_BACKSPACE:
                self.backspace_held = True
                self.backspace_timer = 0.0
            else:
                # capture printable characters
                if event.unicode.isprintable():
                    # enforce max length by focus here for immediate feedback
                    max_chars = self.battle_scene.hero.get_current_stats().focus
                    if len(self.input_text.replace(" ", "")) < max_chars:
                        self.input_text += event.unicode
                        self.error_message = ""
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                self.backspace_held = False
                self.backspace_timer = 0.0

    def _delete_character(self):
        if len(self.input_text) > 0:
            self.input_text = self.input_text[:-1]

    def _build_proposed_action(self) -> ProposedHeroAction:
        # Empty submission -> do nothing action with long time
        if len(self.input_text.strip()) == 0:
            return ProposedHeroAction(
                action="Decided to do nothing this turn.",
                is_valid=True,
                time_to_answer_seconds=100.0,
            )

        n_chars = len(self.input_text.replace(" ", ""))
        focus_limit = self.battle_scene.hero.get_current_stats().focus
        if n_chars > focus_limit:
            return ProposedHeroAction(
                action="",
                is_valid=False,
                time_to_answer_seconds=self.input_timer,
                invalid_reason=(
                    f"Your focus is {focus_limit}; you typed {n_chars} non-space characters."
                ),
            )

        return ProposedHeroAction(
            action=self.input_text,
            is_valid=True,
            time_to_answer_seconds=self.input_timer,
        )

    def update(self, dt: float):
        # track input time
        self.input_timer += dt

        # Handle backspace hold
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

        if self.submit_requested:
            self.submit_requested = False
            proposed_action = self._build_proposed_action()
            if not proposed_action.is_valid:
                self.error_message = proposed_action.invalid_reason or "Invalid action."
                # reset timer for next attempt
                self.input_timer = 0.0
                return

            self.error_message = ""
            self.battle_scene.pending_hero_action = proposed_action
            self.input_text = ""
            self.input_timer = 0.0
            self.battle_scene.change_state(BattleStates.HERO_THINKING)

    def _render_stats(self, screen: pygame.Surface):
        hero = self.battle_scene.hero
        enemy = self.battle_scene.enemy

        hero_name = self.battle_scene.game.theme.fonts["large"].render(
            hero.name or "Hero", True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(hero_name, hero_name.get_rect(topleft=(40, 60)))
        draw_hp_bar(
            screen=screen,
            theme=self.battle_scene.game.theme,
            x=40,
            y=110,
            hp=hero.hp,
            max_hp=hero.get_current_stats().max_hp,
        )

        enemy_name = self.battle_scene.game.theme.fonts["large"].render(
            enemy.name, True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(
            enemy_name, enemy_name.get_rect(topright=(screen.get_width() - 40, 60))
        )
        draw_hp_bar(
            screen=screen,
            theme=self.battle_scene.game.theme,
            x=screen.get_width() - 40 - 180,
            y=110,
            hp=enemy.hp,
            max_hp=enemy.get_current_stats().max_hp,
        )

    def _render_battle_log(self, screen: pygame.Surface):
        return

    def _render_input_box(self, screen: pygame.Surface):
        focus_limit = self.battle_scene.hero.get_current_stats().focus
        remaining_chars = max(focus_limit - len(self.input_text.replace(" ", "")), 0)
        prompt = f"Focus: {remaining_chars}/{focus_limit} characters remaining."
        prompt_surface = self.battle_scene.game.theme.fonts["small"].render(
            prompt, True, self.battle_scene.game.theme.colors["text_hint"]
        )
        screen.blit(prompt_surface, (60, 200))

        box_width = screen.get_width() - 120
        box_height = 48
        box_rect = pygame.Rect(60, 230, box_width, box_height)
        pygame.draw.rect(
            screen, self.battle_scene.game.theme.colors["text"], box_rect, 2
        )

        display_text = self.input_text + "|"
        text_surface = self.battle_scene.game.theme.fonts["medium"].render(
            display_text, True, self.battle_scene.game.theme.colors["text_selected"]
        )
        screen.blit(text_surface, (70, 240))

        if self.error_message:
            error_surface = self.battle_scene.game.theme.fonts["small"].render(
                self.error_message, True, (255, 60, 60)
            )
            screen.blit(error_surface, (60, 285))

        enter_surface = self.battle_scene.game.theme.fonts["small"].render(
            "Press Enter to act", True, self.battle_scene.game.theme.colors["text_hint"]
        )
        screen.blit(
            enter_surface,
            enter_surface.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - 50)
            ),
        )

    def render(self, screen: pygame.Surface):
        screen.fill(self.battle_scene.game.theme.colors["background"])
        self._render_stats(screen)
        self._render_battle_log(screen)
        self._render_input_box(screen)
