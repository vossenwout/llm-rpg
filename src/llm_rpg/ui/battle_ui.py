from __future__ import annotations
import pygame

from llm_rpg.systems.battle.battle_log import BattleEvent
from llm_rpg.systems.hero.hero import Hero
from llm_rpg.systems.battle.enemy import Enemy
from llm_rpg.utils.theme import Theme
from llm_rpg.ui.components import (
    wrap_text_lines,
    draw_text_panel,
    measure_text_block,
    draw_paginated_panel,
    PagedTextState,
)


HP_BAR_WIDTH = 180
HP_BAR_HEIGHT = 16
HP_LABEL_OFFSET = 12
CARD_PADDING = 10
CARD_LINE_HEIGHT = 22
CARD_BORDER = 2
DOTS_PERIOD = 0.25


def draw_hp_bar(
    screen: pygame.Surface,
    theme: Theme,
    x: int,
    y: int,
    hp: int,
    max_hp: int,
    width: int | None = None,
):
    bar_width = width or HP_BAR_WIDTH
    bar_height = HP_BAR_HEIGHT
    pct = max(hp, 0) / max(max_hp, 1)
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, int(bar_width * pct), bar_height)
    pygame.draw.rect(screen, theme.colors["text"], outline_rect, CARD_BORDER)
    pygame.draw.rect(screen, (80, 200, 120), fill_rect)
    hp_text = f"{max(hp, 0)}/{max_hp}"
    hp_surface = theme.fonts["small"].render(hp_text, True, theme.colors["text"])
    screen.blit(
        hp_surface,
        hp_surface.get_rect(
            center=(x + bar_width // 2, y + bar_height + HP_LABEL_OFFSET)
        ),
    )


def build_event_lines(
    event: BattleEvent,
    panel_width: int,
    font: pygame.font.Font,
    padding: int,
) -> list[str]:
    max_width = panel_width - 2 * padding
    lines: list[str] = []
    effect_line = f"{event.effect_description}"
    lines += wrap_text_lines(effect_line, font, max_width)
    return lines


def render_event_card(
    screen: pygame.Surface,
    theme: Theme,
    event: BattleEvent,
    paged_state: PagedTextState,
    prompt_text: str | None = None,
) -> pygame.Rect:
    padding = theme.spacing(2)
    line_spacing = theme.spacing(1)
    small_font = theme.fonts["small"]
    margin = theme.spacing(4)
    panel_width = screen.get_width() - margin * 2
    lines = build_event_lines(event, panel_width, small_font, padding)
    if paged_state.lines != lines:
        paged_state.lines = lines
        paged_state.reset()
    line_height = small_font.get_linesize() + line_spacing
    text_height = line_height * paged_state.lines_per_page - line_spacing
    panel_height = text_height + padding * 2
    panel_y = screen.get_height() - panel_height - margin
    panel_rect = pygame.Rect(margin, panel_y, panel_width, panel_height)
    prompt_to_draw = prompt_text if paged_state.is_last_page else None
    draw_paginated_panel(
        screen=screen,
        rect=panel_rect,
        theme=theme,
        font=small_font,
        paged_state=paged_state,
        padding=padding,
        line_spacing=line_spacing,
        prompt_text=prompt_to_draw,
    )
    return panel_rect


def render_event_ribbon(
    screen: pygame.Surface,
    theme: Theme,
    event: BattleEvent,
    card_rect: pygame.Rect,
) -> pygame.Rect:
    padding = theme.spacing(2)
    line_spacing = theme.spacing(1)
    small_font = theme.fonts["small"]
    feasibility_pct = f"{event.damage_calculation_result.feasibility * 10}%"
    potential_pct = f"{event.damage_calculation_result.potential_damage * 10}%"
    total_damage = event.damage_calculation_result.total_dmg
    line = f"Total DMG {total_damage}: Feasibility {feasibility_pct} Potential DMG {potential_pct}"
    ribbon_width = card_rect.width
    ribbon_x = card_rect.x
    ribbon_text_color = theme.colors["text_hint"]
    ribbon_rect = draw_text_panel(
        screen=screen,
        lines=[line],
        font=small_font,
        theme=theme,
        x=ribbon_x,
        y=card_rect.top - small_font.get_linesize() - padding * 2 - line_spacing,
        padding=padding,
        line_spacing=line_spacing,
        align="center",
        width=ribbon_width,
        draw_border=True,
        text_color=ribbon_text_color,
    )
    return ribbon_rect


def render_stats_row(
    screen: pygame.Surface,
    theme: Theme,
    hero: Hero,
    enemy: Enemy,
):
    padding = theme.spacing(2)
    small_font = theme.fonts["small"]
    line_spacing = theme.spacing(1)

    hero_lines = [
        hero.name or "Hero",
        f"HP: {max(hero.hp, 0)}/{hero.get_current_stats().max_hp}",
    ]
    draw_text_panel(
        screen=screen,
        lines=hero_lines,
        font=small_font,
        theme=theme,
        x=padding,
        y=padding,
        padding=padding,
        line_spacing=line_spacing,
        align="left",
        draw_border=True,
    )

    enemy_lines = [
        enemy.name,
        f"HP: {max(enemy.hp, 0)}/{enemy.get_current_stats().max_hp}",
    ]
    text_width, text_height = measure_text_block(enemy_lines, small_font, line_spacing)
    enemy_panel_width = text_width + padding * 2
    enemy_x = screen.get_width() - padding - enemy_panel_width
    draw_text_panel(
        screen=screen,
        lines=enemy_lines,
        font=small_font,
        theme=theme,
        x=enemy_x,
        y=padding,
        padding=padding,
        line_spacing=line_spacing,
        align="right",
        width=enemy_panel_width,
        draw_border=True,
    )


def render_items_panel(
    screen: pygame.Surface,
    theme: Theme,
    hero: Hero,
    proc_impacts: dict[str, int] | None = None,
):
    padding = theme.spacing(2)
    small_font = theme.fonts["small"]
    line_spacing = theme.spacing(1)
    items = getattr(hero.inventory, "items", [])
    if not items:
        return

    hero_lines = [
        hero.name or "Hero",
        f"HP: {max(hero.hp, 0)}/{hero.get_current_stats().max_hp}",
    ]
    hero_text_width, hero_text_height = measure_text_block(
        hero_lines, small_font, line_spacing
    )
    hero_panel_width = hero_text_width + padding * 2
    hero_panel_height = hero_text_height + padding * 2

    lines: list[str] = []
    for item in items:
        if proc_impacts is None:
            lines.append(item.name)
            continue
        impact = proc_impacts.get(item.name)
        if impact is None or impact == 0:
            lines.append(item.name)
        elif impact > 0:
            lines.append(f"{item.name} (+{impact})")
        else:
            lines.append(f"{item.name} (-{abs(impact)})")

    text_width, text_height = measure_text_block(lines, small_font, line_spacing)
    panel_width = max(hero_panel_width, text_width + padding * 2)
    panel_height = text_height + padding * 2
    x = theme.spacing(0)
    y = padding + hero_panel_height + theme.spacing(1)

    draw_text_panel(
        screen=screen,
        lines=lines,
        font=small_font,
        theme=theme,
        x=x,
        y=y,
        padding=padding,
        line_spacing=line_spacing,
        align="left",
        width=panel_width,
        min_height=panel_height,
        draw_border=False,
        text_color=theme.colors["text_items"],
    )


def prompt_for_battle_end(is_finishing: bool) -> str | None:
    return None


def advance_dots(dots: int, dot_timer: float, dt: float):
    dot_timer += dt
    if dot_timer >= DOTS_PERIOD:
        dot_timer -= DOTS_PERIOD
        dots = (dots + 1) % 4
    return dots, dot_timer


def render_processing_text(screen: pygame.Surface, theme: Theme, text: str, dots: int):
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
