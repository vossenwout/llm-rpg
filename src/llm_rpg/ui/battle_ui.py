from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import pygame

from llm_rpg.objects.item import LLMScalingBoost, ProcCondition
from llm_rpg.systems.battle.battle_log import BattleEvent
from llm_rpg.systems.battle.damage_calculator import BonusMultiplierDamage
from llm_rpg.systems.hero.hero import Hero
from llm_rpg.systems.battle.enemy import Enemy
from llm_rpg.utils.theme import Theme
from llm_rpg.ui.components import wrap_text_lines, draw_text_panel, measure_text_block


HP_BAR_WIDTH = 180
HP_BAR_HEIGHT = 16
HP_LABEL_OFFSET = 12
CARD_PADDING = 10
CARD_BORDER = 2
CARD_LINE_HEIGHT = 22
CARD_BOTTOM_PADDING = 16
STATS_LEFT_POS = (0, 0)
STATS_BAR_Y = 20
DOTS_PERIOD = 0.25


class DetailLevel(Enum):
    BASIC = "basic"
    DEBUG = "debug"


@dataclass
class IconSet:
    damage: pygame.Surface | None = None
    proc: pygame.Surface | None = None
    feasibility: pygame.Surface | None = None
    potential: pygame.Surface | None = None
    speed: pygame.Surface | None = None
    new_word: pygame.Surface | None = None
    overused: pygame.Surface | None = None


@dataclass
class ScrollableTextState:
    offset: int = 0
    visible_rows: int | None = None


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


def _format_proc_line(bonus: BonusMultiplierDamage) -> str:
    trigger = (
        f"{bonus.bonus_multiplier.proc_reason.proc_condition.value}="
        f"{bonus.bonus_multiplier.proc_reason.condition_value}"
    )
    multiplier = bonus.bonus_multiplier.multiplier
    impact = bonus.damage_impact
    sign = "+" if impact >= 0 else "-"
    return (
        f"{bonus.bonus_multiplier.item_name} ({bonus.bonus_multiplier.boost_name}) — "
        f"{trigger} ⇒ x{multiplier:.2f} ⇒ {sign}{abs(impact)}"
    )


def _format_scaling_boosts(
    feasibility_boosts: list[LLMScalingBoost],
    potential_boosts: list[LLMScalingBoost],
) -> list[str]:
    lines: list[str] = []
    for boost in feasibility_boosts:
        lines.append(
            f"Feasibility boost: {boost.item_name} {boost.boost_name} "
            f"{boost.base_scaling:.2f}→{boost.boosted_scaling:.2f}"
        )
    for boost in potential_boosts:
        lines.append(
            f"Potential boost: {boost.item_name} {boost.boost_name} "
            f"{boost.base_scaling:.2f}→{boost.boosted_scaling:.2f}"
        )
    return lines


def _aggregate_proc_multiplier(
    procs: list[BonusMultiplierDamage],
    condition: ProcCondition,
) -> float:
    total = 0.0
    for proc in procs:
        if proc.bonus_multiplier.proc_reason.proc_condition == condition:
            total += proc.bonus_multiplier.multiplier
    return total


def build_hero_event_lines(
    event: BattleEvent,
    panel_width: int,
    font: pygame.font.Font,
    detail_level: DetailLevel,
) -> tuple[list[str], list[str]]:
    result = event.damage_calculation_result
    main_lines: list[str] = []
    debug_lines: list[str] = []

    max_width = panel_width - 2 * CARD_PADDING

    def add_wrapped(text: str, max_lines: int = 2):
        main_lines.extend(wrap_text_lines(text, font, max_width, max_lines))

    def add_wrapped_indented(text: str, indent: str = "  ", max_lines: int = 2):
        wrapped = wrap_text_lines(text, font, max_width, max_lines)
        main_lines.extend([f"{indent}{line}" for line in wrapped])

    header = f"{event.character_name} acts!"
    action_line = f"Action: {event.proposed_action}"
    effect_line = f"Effect: {event.effect_description}"
    dmg_line = f"Damage: {result.total_dmg}"

    main_lines += wrap_text_lines(header, font, max_width, 1)
    main_lines += wrap_text_lines(action_line, font, max_width, 4)
    main_lines += wrap_text_lines(effect_line, font, max_width, 4)
    add_wrapped(dmg_line, 1)
    add_wrapped("Damage breakdown:", 1)

    feasibility_pct = result.feasibility * 100
    potential_pct = result.potential_damage * 100
    add_wrapped_indented(f"Feasibility: {feasibility_pct:.1f}%", max_lines=1)
    add_wrapped_indented(f"Potential damage: {potential_pct:.1f}%", max_lines=1)

    speed_multiplier = _aggregate_proc_multiplier(
        result.applied_bonus_multiplier_damages, ProcCondition.ANSWER_SPEED_S
    )
    new_word_multiplier = _aggregate_proc_multiplier(
        result.applied_bonus_multiplier_damages, ProcCondition.N_NEW_WORDS_IN_ACTION
    )
    overused_multiplier = _aggregate_proc_multiplier(
        result.applied_bonus_multiplier_damages,
        ProcCondition.N_OVERUSED_WORDS_IN_ACTION,
    )

    add_wrapped_indented(
        f"Answer speed: {result.answer_speed_s:.1f}s ⇒ {speed_multiplier * 100:+.0f}%",
        max_lines=2,
    )
    add_wrapped_indented(
        f"New words: {result.n_new_words_in_action} ⇒ {new_word_multiplier * 100:+.0f}%",
        max_lines=2,
    )
    add_wrapped_indented(
        f"Overused words: {result.n_overused_words_in_action} ⇒ {overused_multiplier * 100:+.0f}%",
        max_lines=2,
    )

    for boost_line in _format_scaling_boosts(
        result.applied_feasibility_boosts, result.applied_potential_damage_boosts
    ):
        add_wrapped_indented(boost_line, max_lines=2)

    if result.applied_bonus_multiplier_damages:
        add_wrapped_indented("Item procs:", indent="  ", max_lines=1)
        for proc in result.applied_bonus_multiplier_damages:
            add_wrapped_indented(_format_proc_line(proc), indent="    ", max_lines=3)

    if detail_level is DetailLevel.DEBUG:
        debug_lines.append(f"Base damage: {result.base_dmg}")
        debug_lines.append(f"Random factor: {result.random_factor}")
        debug_lines.append(f"LLM scaling: {result.llm_dmg_scaling}")
        debug_lines.append(f"LLM scaled base dmg: {result.llm_scaled_base_dmg}")
        bonus_sum = sum(
            p.damage_impact for p in result.applied_bonus_multiplier_damages
        )
        debug_lines.append(f"Bonus sum: {bonus_sum}")
        debug_lines.append(f"Total damage: {result.total_dmg}")

    return main_lines, debug_lines


def build_enemy_event_lines(
    event: BattleEvent,
    panel_width: int,
    font: pygame.font.Font,
) -> list[str]:
    lines: list[str] = []
    header = f"{event.character_name} acts!"
    action_line = f"Action: {event.proposed_action}"
    effect_line = f"Effect: {event.effect_description}"
    dmg_line = f"Damage: {event.damage_calculation_result.total_dmg}"
    lines += wrap_text_lines(header, font, panel_width - 2 * CARD_PADDING, 1)
    lines += wrap_text_lines(action_line, font, panel_width - 2 * CARD_PADDING, 4)
    lines += wrap_text_lines(effect_line, font, panel_width - 2 * CARD_PADDING, 4)
    lines.append(dmg_line)
    return lines


def _render_lines(
    screen: pygame.Surface,
    theme: Theme,
    lines: list[str],
    panel_x: int,
    panel_y: int,
    panel_width: int,
    prompt_text: str | None,
    scroll_state: ScrollableTextState,
):
    small_font = theme.fonts["small"]
    visible_lines = lines
    if scroll_state.visible_rows is not None:
        start = max(0, scroll_state.offset)
        end = min(len(lines), start + scroll_state.visible_rows)
        visible_lines = lines[start:end]
    card_height = CARD_LINE_HEIGHT * len(visible_lines) + CARD_BOTTOM_PADDING
    max_y = screen.get_height() - card_height - CARD_BOTTOM_PADDING
    adjusted_panel_y = min(panel_y, max_y)
    card_rect = pygame.Rect(panel_x, adjusted_panel_y, panel_width, card_height)
    pygame.draw.rect(screen, theme.colors["text"], card_rect, CARD_BORDER)
    text_y = adjusted_panel_y + CARD_PADDING
    for line in visible_lines:
        surf = small_font.render(line, True, theme.colors["text"])
        screen.blit(surf, (panel_x + CARD_PADDING, text_y))
        text_y += CARD_LINE_HEIGHT
    if prompt_text:
        prompt_surf = small_font.render(prompt_text, True, theme.colors["text_hint"])
        screen.blit(
            prompt_surf,
            prompt_surf.get_rect(
                center=(screen.get_width() // 2, card_rect.bottom + 24)
            ),
        )


def render_event_hero(
    screen: pygame.Surface,
    theme: Theme,
    event: BattleEvent,
    panel_x: int,
    panel_y: int,
    panel_width: int,
    detail_level: DetailLevel,
    prompt_text: str | None = None,
    scroll_state: ScrollableTextState | None = None,
):
    small_font = theme.fonts["small"]
    main_lines, debug_lines = build_hero_event_lines(
        event=event,
        panel_width=panel_width,
        font=small_font,
        detail_level=detail_level,
    )
    lines = main_lines + debug_lines
    state = scroll_state or ScrollableTextState()
    _render_lines(
        screen=screen,
        theme=theme,
        lines=lines,
        panel_x=panel_x,
        panel_y=panel_y,
        panel_width=panel_width,
        prompt_text=prompt_text,
        scroll_state=state,
    )


def render_event_enemy(
    screen: pygame.Surface,
    theme: Theme,
    event: BattleEvent,
    panel_x: int,
    panel_y: int,
    panel_width: int,
    prompt_text: str | None = None,
):
    small_font = theme.fonts["small"]
    lines = build_enemy_event_lines(
        event=event,
        panel_width=panel_width,
        font=small_font,
    )
    _render_lines(
        screen=screen,
        theme=theme,
        lines=lines,
        panel_x=panel_x,
        panel_y=panel_y,
        panel_width=panel_width,
        prompt_text=prompt_text,
        scroll_state=ScrollableTextState(),
    )


def render_event_card(
    screen: pygame.Surface,
    theme: Theme,
    event: BattleEvent,
    panel_x: int,
    panel_y: int,
    panel_width: int,
    debug_mode: bool,
    prompt_text: str | None = None,
    scroll_state: ScrollableTextState | None = None,
):
    if event.is_hero_turn:
        detail_level = DetailLevel.DEBUG if debug_mode else DetailLevel.BASIC
        render_event_hero(
            screen=screen,
            theme=theme,
            event=event,
            panel_x=panel_x,
            panel_y=panel_y,
            panel_width=panel_width,
            detail_level=detail_level,
            prompt_text=prompt_text,
            scroll_state=scroll_state,
        )
    else:
        render_event_enemy(
            screen=screen,
            theme=theme,
            event=event,
            panel_x=panel_x,
            panel_y=panel_y,
            panel_width=panel_width,
            prompt_text=prompt_text,
        )


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
    x = padding
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


def prompt_for_battle_end(is_finishing: bool):
    return "Press Enter to finish battle" if is_finishing else "Press Enter to continue"


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
