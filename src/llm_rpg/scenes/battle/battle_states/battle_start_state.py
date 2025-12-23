from __future__ import annotations

import queue
import threading
import pygame
from typing import TYPE_CHECKING

from llm_rpg.scenes.battle.battle_states.battle_states import BattleStates
from llm_rpg.scenes.state import State
from llm_rpg.ui.components import draw_text_panel
from llm_rpg.ui.battle_ui import advance_dots
from llm_rpg.ui.backgrounds import build_battle_background
from llm_rpg.systems.battle.enemy_scaling import scale_enemy
from llm_rpg.systems.battle.enemy import Enemy

if TYPE_CHECKING:
    from llm_rpg.scenes.battle.battle_scene import BattleScene


class BattleStartState(State):
    def __init__(self, battle_scene: BattleScene):
        self.battle_scene = battle_scene
        self.battle_scene.background = None
        self.ready_to_start = False
        self.enemy_generation_result_queue: queue.Queue[
            tuple[Enemy, pygame.Surface] | Exception
        ] = queue.Queue(maxsize=1)
        self.loading_started = False
        self.loading_done = False
        self.loading_error: str | None = None
        self.dots = 0
        self.dot_timer = 0.0
        self.max_wait = 120.0
        self.animation_timer = 0.0

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.ready_to_start = True

    def update(self, dt: float):
        self.battle_scene.update_background(dt)
        self.animation_timer += dt
        self.dots, self.dot_timer = advance_dots(
            dots=self.dots,
            dot_timer=self.dot_timer,
            dt=dt,
        )

        if not self.loading_started:
            self.loading_started = True
            thread = threading.Thread(target=self._generate_enemy, daemon=True)
            thread.start()

        if not self.loading_done:
            try:
                result = self.enemy_generation_result_queue.get_nowait()
                if isinstance(result, Exception):
                    self.loading_error = str(result)
                else:
                    enemy, sprite = result
                    self.battle_scene.enemy = enemy
                    self.battle_scene.enemy_sprite = sprite
                    self.battle_scene.background = build_battle_background(
                        enemy_name=enemy.name,
                        config=self.battle_scene.game.config.battle_background_config,
                    )
                self.loading_done = True
            except queue.Empty:
                if self.animation_timer >= self.max_wait:
                    self.loading_error = "Sprite generation timed out"
                    self.loading_done = True

        if (
            self.loading_done
            and self.ready_to_start
            and self.battle_scene.enemy is not None
        ):
            self.battle_scene.change_state(BattleStates.TURN)

    def render(self, screen: pygame.Surface):
        self.battle_scene.render_background(screen)
        spacing = self.battle_scene.game.theme.spacing

        if not self.loading_done:
            loading_text = "GENERATING ENEMY" + "." * self.dots
            prompt_surface = self.battle_scene.game.theme.fonts["small"].render(
                loading_text,
                True,
                self.battle_scene.game.theme.colors["primary"],
            )
            screen.blit(
                prompt_surface,
                prompt_surface.get_rect(
                    center=(screen.get_width() // 2, screen.get_height() // 2)
                ),
            )
            return

        enemy = self.battle_scene.enemy
        if enemy is None:
            prompt_surface = self.battle_scene.game.theme.fonts["small"].render(
                "Enemy generation failed",
                True,
                (255, 80, 80),
            )
            screen.blit(
                prompt_surface,
                prompt_surface.get_rect(
                    center=(screen.get_width() // 2, screen.get_height() - spacing(6))
                ),
            )
            return

        title = self.battle_scene.game.theme.fonts["medium"].render(
            "An enemy appears", True, self.battle_scene.game.theme.colors["primary"]
        )
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, spacing(8))))

        enemy_name = self.battle_scene.game.theme.fonts["medium"].render(
            enemy.name, True, self.battle_scene.game.theme.colors["primary"]
        )
        enemy_name_rect = enemy_name.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 - spacing(3))
        )
        screen.blit(enemy_name, enemy_name_rect)

        description_max_width = screen.get_width() - spacing(6)
        draw_text_panel(
            screen=screen,
            lines=enemy.description,
            font=self.battle_scene.game.theme.fonts["small"],
            theme=self.battle_scene.game.theme,
            x=None,
            y=enemy_name_rect.bottom + spacing(2),
            max_width=description_max_width,
            auto_wrap=True,
            draw_border=False,
        )

        if self.loading_error:
            prompt_surface = self.battle_scene.game.theme.fonts["small"].render(
                f"Error: {self.loading_error}",
                True,
                (255, 80, 80),
            )
        else:
            prompt_surface = self.battle_scene.game.theme.fonts["small"].render(
                "Press ENTER to start battle",
                True,
                self.battle_scene.game.theme.colors["text_hint"],
            )

        screen.blit(
            prompt_surface,
            prompt_surface.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - spacing(6))
            ),
        )

    def _generate_enemy(self):
        try:
            enemy, sprite = self.battle_scene.game.enemy_generator.generate_enemy()
            scale_enemy(
                enemy=enemy,
                battles_won=self.battle_scene.game.battles_won,
                game_config=self.battle_scene.game.config,
                debug=self.battle_scene.game.config.debug_mode,
            )
            self.enemy_generation_result_queue.put((enemy, sprite))
        except Exception as exc:
            self.enemy_generation_result_queue.put(exc)
