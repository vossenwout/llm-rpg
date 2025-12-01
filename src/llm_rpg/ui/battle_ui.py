from __future__ import annotations
import pygame

from llm_rpg.systems.battle.battle_log import BattleEvent
from llm_rpg.utils.theme import Theme


class BattleUIConfig:
    hp_bar_width: int = 180
    hp_bar_height: int = 16
    hp_label_offset: int = 12
    card_padding: int = 10
    card_border: int = 2
    card_line_height: int = 22
    card_bottom_padding: int = 16
    stats_left_pos = (40, 60)
    stats_bar_y = 110
    stats_bar_offset = 180
    prompt_offset = 24
    dots_period = 0.25


def draw_hp_bar(
    screen: pygame.Surface,
    theme,
    x: int,
    y: int,
    hp: int,
    max_hp: int,
    width: int | None = None,
    config: BattleUIConfig | None = None,
):
    cfg = config or BattleUIConfig()
    bar_width = width or cfg.hp_bar_width
    bar_height = cfg.hp_bar_height
    pct = max(hp, 0) / max(max_hp, 1)
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, int(bar_width * pct), bar_height)
    pygame.draw.rect(screen, theme.colors["text"], outline_rect, cfg.card_border)
    pygame.draw.rect(screen, (80, 200, 120), fill_rect)
    hp_text = f"{max(hp, 0)}/{max_hp}"
    hp_surface = theme.fonts["small"].render(hp_text, True, theme.colors["text"])
    screen.blit(
        hp_surface,
        hp_surface.get_rect(
            center=(x + bar_width // 2, y + bar_height + cfg.hp_label_offset)
        ),
    )


def wrap_text_lines(
    text: str,
    font: pygame.font.Font,
    max_width: int,
    max_lines: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if current == "" else f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
        if len(lines) == max_lines:
            break
    if len(lines) < max_lines and current:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    if len(lines) == max_lines and words and " ".join(words) != " ".join(lines):
        lines[-1] = (
            lines[-1][: max(0, len(lines[-1]) - 3)] + "..."
            if len(lines[-1]) > 3
            else "..."
        )
    return lines


def render_event_card(
    screen: pygame.Surface,
    theme: Theme,
    event: BattleEvent,
    panel_x: int,
    panel_y: int,
    panel_width: int,
    debug_mode: bool,
    prompt_text: str | None = None,
    config: BattleUIConfig | None = None,
):
    cfg = config or BattleUIConfig()
    small_font = theme.fonts["small"]

    header = f"{'🦸' if event.is_hero_turn else '👾'} {event.character_name} acts!"
    action_line = f"Action: {event.proposed_action}"
    effect_line = f"Effect: {event.effect_description}"
    dmg_line = f"Damage: {event.damage_calculation_result.total_dmg}"
    debug_line = ""
    if debug_mode:
        debug_line = (
            f"F:{event.damage_calculation_result.feasibility} "
            f"P:{event.damage_calculation_result.potential_damage}"
        )

    content_lines: list[str] = []
    content_lines += wrap_text_lines(
        header, small_font, panel_width - 2 * cfg.card_padding, 1
    )
    content_lines += wrap_text_lines(
        action_line, small_font, panel_width - 2 * cfg.card_padding, 4
    )
    content_lines += wrap_text_lines(
        effect_line, small_font, panel_width - 2 * cfg.card_padding, 4
    )
    content_lines += wrap_text_lines(
        dmg_line, small_font, panel_width - 2 * cfg.card_padding, 1
    )
    if debug_line:
        content_lines += wrap_text_lines(
            debug_line, small_font, panel_width - 2 * cfg.card_padding, 1
        )

    card_height = cfg.card_line_height * len(content_lines) + cfg.card_bottom_padding
    card_rect = pygame.Rect(panel_x, panel_y, panel_width, card_height)
    pygame.draw.rect(screen, theme.colors["text"], card_rect, cfg.card_border)

    text_y = panel_y + cfg.card_padding
    for line in content_lines:
        surf = small_font.render(line, True, theme.colors["text"])
        screen.blit(surf, (panel_x + cfg.card_padding, text_y))
        text_y += cfg.card_line_height

    if prompt_text:
        prompt_surf = small_font.render(prompt_text, True, theme.colors["text_hint"])
        screen.blit(
            prompt_surf,
            prompt_surf.get_rect(
                center=(screen.get_width() // 2, card_rect.bottom + 24)
            ),
        )


def render_stats_row(
    screen: pygame.Surface,
    theme,
    hero,
    enemy,
    config: BattleUIConfig | None = None,
):
    cfg = config or BattleUIConfig()
    hero_name = theme.fonts["large"].render(
        hero.name or "Hero", True, theme.colors["text"]
    )
    screen.blit(hero_name, hero_name.get_rect(topleft=cfg.stats_left_pos))
    draw_hp_bar(
        screen=screen,
        theme=theme,
        x=cfg.stats_left_pos[0],
        y=cfg.stats_bar_y,
        hp=hero.hp,
        max_hp=hero.get_current_stats().max_hp,
        width=cfg.hp_bar_width,
        config=cfg,
    )

    enemy_name = theme.fonts["large"].render(enemy.name, True, theme.colors["text"])
    enemy_name_rect = enemy_name.get_rect(
        topright=(screen.get_width() - cfg.stats_left_pos[0], cfg.stats_left_pos[1])
    )
    screen.blit(enemy_name, enemy_name_rect)
    draw_hp_bar(
        screen=screen,
        theme=theme,
        x=screen.get_width() - cfg.stats_left_pos[0] - cfg.hp_bar_width,
        y=cfg.stats_bar_y,
        hp=enemy.hp,
        max_hp=enemy.get_current_stats().max_hp,
        width=cfg.hp_bar_width,
        config=cfg,
    )


def prompt_for_battle_end(is_finishing: bool):
    return "Press Enter to finish battle" if is_finishing else "Press Enter to continue"


def advance_dots(dots: int, dot_timer: float, dt: float, period: float):
    dot_timer += dt
    if dot_timer >= period:
        dot_timer -= period
        dots = (dots + 1) % 4
    return dots, dot_timer


def render_processing_text(screen: pygame.Surface, theme, text: str, dots: int):
    dotted_text = f"{text}{'.' * dots}"
    prompt_surface = theme.fonts["medium"].render(
        dotted_text, True, theme.colors["text_selected"]
    )
    screen.blit(
        prompt_surface,
        prompt_surface.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - 100)
        ),
    )
