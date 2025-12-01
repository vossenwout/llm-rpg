from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.battle.battle_states.battle_states import BattleStates
from llm_rpg.systems.battle.damage_calculator import DamageCalculationResult
from llm_rpg.systems.hero.hero import ProposedHeroAction
from llm_rpg.systems.battle.battle_log import BattleEvent
from llm_rpg.scenes.state import State
from llm_rpg.utils.ui import draw_panel, draw_blinking_cursor

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

    def _update_hero_turn(self, proposed_action: ProposedHeroAction):
        action_effect = self.battle_scene.battle_ai.determine_action_effect(
            proposed_action_attacker=proposed_action.action,
            hero=self.battle_scene.hero,
            enemy=self.battle_scene.enemy,
            is_hero_attacker=True,
            battle_log_string=self.battle_scene.battle_log.to_string_for_battle_ai(),
        )

        n_new_words_in_action = (
            self.battle_scene.creativity_tracker.count_new_words_in_action(
                action=proposed_action.action
            )
        )
        n_overused_words_in_action = (
            self.battle_scene.creativity_tracker.count_overused_words_in_action(
                action=proposed_action.action
            )
        )
        damage_calculation_result: DamageCalculationResult = (
            self.battle_scene.damage_calculator.calculate_damage(
                attack=self.battle_scene.hero.get_current_stats().attack,
                defense=self.battle_scene.enemy.get_current_stats().defense,
                feasibility=action_effect.feasibility,
                potential_damage=action_effect.potential_damage,
                n_new_words_in_action=n_new_words_in_action,
                n_overused_words_in_action=n_overused_words_in_action,
                answer_speed_s=proposed_action.time_to_answer_seconds,
                equiped_items=self.battle_scene.hero.inventory.items,
            )
        )
        self.battle_scene.enemy.inflict_damage(damage_calculation_result.total_dmg)
        self.battle_scene.creativity_tracker.add_action(proposed_action.action)
        self.battle_scene.battle_log.add_event(
            BattleEvent(
                is_hero_turn=True,
                character_name=self.battle_scene.hero.name,
                proposed_action=proposed_action.action,
                effect_description=action_effect.effect_description,
                damage_calculation_result=damage_calculation_result,
            )
        )

    def _update_enemy_turn(self):
        proposed_enemy_action = self.battle_scene.enemy.get_next_action(
            self.battle_scene.battle_log, self.battle_scene.hero
        )
        action_effect = self.battle_scene.battle_ai.determine_action_effect(
            proposed_action_attacker=proposed_enemy_action,
            hero=self.battle_scene.hero,
            enemy=self.battle_scene.enemy,
            is_hero_attacker=False,
            battle_log_string=self.battle_scene.battle_log.to_string_for_battle_ai(),
        )
        damage_calculation_result = (
            self.battle_scene.damage_calculator.calculate_damage(
                attack=self.battle_scene.enemy.get_current_stats().attack,
                defense=self.battle_scene.hero.get_current_stats().defense,
                feasibility=action_effect.feasibility,
                potential_damage=action_effect.potential_damage,
                n_new_words_in_action=0,
                n_overused_words_in_action=0,
                answer_speed_s=1000,
                equiped_items=[],
            )
        )

        self.battle_scene.hero.inflict_damage(damage_calculation_result.total_dmg)

        self.battle_scene.battle_log.add_event(
            BattleEvent(
                is_hero_turn=False,
                character_name=self.battle_scene.enemy.name,
                proposed_action=proposed_enemy_action,
                effect_description=action_effect.effect_description,
                damage_calculation_result=damage_calculation_result,
            )
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
            self._update_hero_turn(proposed_action)
            if self.battle_scene.enemy.is_dead():
                self.battle_scene.change_state(BattleStates.END)
                return

            self._update_enemy_turn()
            if self.battle_scene.hero.is_dead():
                self.battle_scene.change_state(BattleStates.END)
                return

            # prepare for next turn input
            self.input_text = ""
            self.input_timer = 0.0

    def _draw_hp_bar(
        self, screen: pygame.Surface, x: int, y: int, hp: int, max_hp: int
    ):
        bar_width = 180
        bar_height = 16
        pct = max(hp, 0) / max(max_hp, 1)
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        fill_rect = pygame.Rect(x, y, int(bar_width * pct), bar_height)
        pygame.draw.rect(
            screen, self.battle_scene.game.theme.colors["text"], outline_rect, 2
        )
        pygame.draw.rect(screen, (80, 200, 120), fill_rect)

    def _render_stats(self, screen: pygame.Surface):
        hero = self.battle_scene.hero
        enemy = self.battle_scene.enemy

        hero_panel = pygame.Rect(40, 40, 320, 140)
        enemy_panel = pygame.Rect(screen.get_width() - 360, 40, 320, 140)
        draw_panel(screen, hero_panel, self.battle_scene.game.theme)
        draw_panel(screen, enemy_panel, self.battle_scene.game.theme)

        hero_name = self.battle_scene.game.theme.fonts["large"].render(
            hero.name or "Hero", True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(
            hero_name,
            hero_name.get_rect(center=(hero_panel.centerx, hero_panel.y + 40)),
        )
        self._draw_hp_bar(
            screen,
            hero_panel.x + 20,
            hero_panel.bottom - 50,
            hero.hp,
            hero.get_current_stats().max_hp,
        )

        enemy_name = self.battle_scene.game.theme.fonts["large"].render(
            enemy.name, True, self.battle_scene.game.theme.colors["text"]
        )
        screen.blit(
            enemy_name,
            enemy_name.get_rect(center=(enemy_panel.centerx, enemy_panel.y + 40)),
        )
        self._draw_hp_bar(
            screen,
            enemy_panel.x + 20,
            enemy_panel.bottom - 50,
            enemy.hp,
            enemy.get_current_stats().max_hp,
        )

    def _render_battle_log(self, screen: pygame.Surface):
        if not self.battle_scene.battle_log.events:
            return
        log_text = self.battle_scene.battle_log.get_string_of_last_events(
            n_events=2, debug_mode=self.battle_scene.game.config.debug_mode
        )
        lines = log_text.splitlines()
        log_panel = pygame.Rect(40, 220, screen.get_width() - 80, 140)
        draw_panel(screen, log_panel, self.battle_scene.game.theme)
        start_y = log_panel.y + 24
        for i, line in enumerate(lines):
            surf = self.battle_scene.game.theme.fonts["small"].render(
                line, True, self.battle_scene.game.theme.colors["text"]
            )
            screen.blit(surf, (log_panel.x + 20, start_y + i * 24))

    def _render_input_box(self, screen: pygame.Surface):
        prompt = f"Your focus allows {self.battle_scene.hero.get_current_stats().focus} characters."
        prompt_surface = self.battle_scene.game.theme.fonts["small"].render(
            prompt, True, self.battle_scene.game.theme.colors["text_hint"]
        )
        input_panel = pygame.Rect(40, 380, screen.get_width() - 80, 120)
        draw_panel(screen, input_panel, self.battle_scene.game.theme)

        screen.blit(prompt_surface, (input_panel.x + 12, input_panel.y - 24))

        text_surface = self.battle_scene.game.theme.fonts["medium"].render(
            self.input_text, True, self.battle_scene.game.theme.colors["text_selected"]
        )
        text_pos = (input_panel.x + 16, input_panel.y + 24)
        screen.blit(text_surface, text_pos)

        cursor_x = text_pos[0] + text_surface.get_width() + 4
        cursor_y = text_pos[1]
        draw_blinking_cursor(
            screen,
            cursor_x,
            cursor_y,
            text_surface.get_height(),
            self.battle_scene.game.theme,
            pygame.time.get_ticks(),
        )

        if self.error_message:
            error_surface = self.battle_scene.game.theme.fonts["small"].render(
                self.error_message, True, (255, 60, 60)
            )
            screen.blit(error_surface, (input_panel.x + 12, input_panel.y + 70))

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
