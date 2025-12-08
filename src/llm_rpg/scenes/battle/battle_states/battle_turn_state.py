from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.battle.battle_states.battle_states import BattleStates
from llm_rpg.systems.hero.hero import ProposedHeroAction
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import draw_input_panel
from llm_rpg.ui.battle_ui import render_stats_row, render_items_panel

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene


class BattleTurnState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.input_text = ""
        self.error_message = ""
        self.submit_requested = False
        self.input_timer = 0.0

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
                if event.unicode.isprintable():
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
            self.error_message = ""

    def _build_proposed_action(self) -> ProposedHeroAction:
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
        self.input_timer += dt

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
                self.input_timer = 0.0
                return

            self.error_message = ""
            self.battle_scene.pending_hero_action = proposed_action
            self.input_text = ""
            self.input_timer = 0.0
            self.battle_scene.change_state(BattleStates.HERO_THINKING)

    def _render_input_box(self, screen: pygame.Surface):
        spacing = self.battle_scene.game.theme.spacing
        panel_rect = draw_input_panel(
            screen=screen,
            current_text=self.input_text,
            font=self.battle_scene.game.theme.fonts["small"],
            theme=self.battle_scene.game.theme,
            x=spacing(0.5),
            y=screen.get_height() - spacing(5),
            width=screen.get_width() - spacing(1),
            padding=spacing(1),
            time_ms=pygame.time.get_ticks(),
        )

        focus_limit = self.battle_scene.hero.get_current_stats().focus
        remaining_chars = max(focus_limit - len(self.input_text.replace(" ", "")), 0)
        focus_meter = f"Focus: {remaining_chars}/{focus_limit} characters remaining."
        prompt_surface = self.battle_scene.game.theme.fonts["small"].render(
            focus_meter, True, self.battle_scene.game.theme.colors["text_hint"]
        )

        prompt_x = panel_rect.x + (panel_rect.width - prompt_surface.get_width()) // 2
        screen.blit(
            prompt_surface,
            (prompt_x, panel_rect.y - spacing(4)),
        )

        if self.error_message:
            error_surface = self.battle_scene.game.theme.fonts["small"].render(
                self.error_message, True, (255, 60, 60)
            )
            screen.blit(
                error_surface,
                (panel_rect.x, panel_rect.bottom + spacing(0.5)),
            )

    def render(self, screen: pygame.Surface):
        screen.fill(self.battle_scene.game.theme.colors["background"])
        render_stats_row(
            screen=screen,
            theme=self.battle_scene.game.theme,
            hero=self.battle_scene.hero,
            enemy=self.battle_scene.enemy,
        )
        render_items_panel(
            screen=screen,
            theme=self.battle_scene.game.theme,
            hero=self.battle_scene.hero,
            proc_impacts=None,
        )
        self._render_input_box(screen)
