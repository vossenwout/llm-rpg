from dataclasses import dataclass
import pygame
from typing import Tuple, List, Optional
from llm_rpg.utils.theme import Theme


@dataclass
class PagedTextState:
    lines: List[str]
    page_index: int = 0
    lines_per_page: int = 2

    @property
    def total_pages(self) -> int:
        if not self.lines:
            return 1
        return (len(self.lines) + self.lines_per_page - 1) // self.lines_per_page

    @property
    def is_last_page(self) -> bool:
        return self.page_index >= self.total_pages - 1

    def current_page_lines(self) -> List[str]:
        start = self.page_index * self.lines_per_page
        end = start + self.lines_per_page
        return self.lines[start:end]

    def next_page(self) -> None:
        if not self.is_last_page:
            self.page_index += 1

    def reset(self) -> None:
        self.page_index = 0


def draw_panel(
    screen: pygame.Surface,
    rect: pygame.Rect | Tuple[int, int, int, int],
    theme: Theme,
    draw_border: bool = True,
):
    base_rect = pygame.Rect(rect)
    outer_thickness = 2
    inner_thickness = 1

    if draw_border:
        pygame.draw.rect(
            screen, theme.colors["border_light"], base_rect, outer_thickness
        )

        inner_rect = base_rect.inflate(-outer_thickness * 2, -outer_thickness * 2)
        pygame.draw.rect(
            screen, theme.colors["border_dark"], inner_rect, inner_thickness
        )

        fill_rect = inner_rect.inflate(-inner_thickness * 2, -inner_thickness * 2)
        pygame.draw.rect(screen, theme.colors["panel_inner"], fill_rect)
    else:
        pygame.draw.rect(screen, theme.colors["panel_inner"], base_rect)


def wrap_text_lines(
    text: str,
    font: pygame.font.Font,
    max_width: int,
    max_lines: int | None = None,
) -> List[str]:
    words = text.split()
    if not words:
        return [""]
    lines: List[str] = []
    current = ""
    for word in words:
        candidate = word if current == "" else f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
        if max_lines and len(lines) == max_lines:
            break
    if (not max_lines or len(lines) < max_lines) and current:
        lines.append(current)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
    if (
        max_lines
        and len(lines) == max_lines
        and words
        and " ".join(words) != " ".join(lines)
    ):
        lines[-1] = (
            lines[-1][: max(0, len(lines[-1]) - 3)] + "..."
            if len(lines[-1]) > 3
            else "..."
        )
    return lines


def measure_text_block(
    lines: List[str], font: pygame.font.Font, line_spacing: int = 0
) -> Tuple[int, int]:
    """
    Calculate the dimensions needed to render a block of text.

    Args:
        lines: List of text lines to measure
        font: Font to use for rendering
        line_spacing: Additional spacing between lines

    Returns:
        (width, height) tuple of the text block dimensions
    """
    if not lines:
        return (0, 0)

    max_width = 0
    total_height = 0

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (255, 255, 255))
        line_width = text_surface.get_width()
        line_height = text_surface.get_height()

        max_width = max(max_width, line_width)
        total_height += line_height

        if i < len(lines) - 1:
            total_height += line_spacing

    return (max_width, total_height)


def draw_text_panel(
    screen: pygame.Surface,
    lines: List[str] | str,
    font: pygame.font.Font,
    theme: Theme,
    x: Optional[int] = None,
    y: Optional[int] = None,
    padding: Optional[int] = None,
    line_spacing: Optional[int] = None,
    text_color: Optional[Tuple[int, int, int]] = None,
    align: str = "center",
    width: Optional[int] = None,
    max_width: Optional[int] = None,
    auto_wrap: bool = False,
    draw_border: bool = True,
    min_height: Optional[int] = None,
) -> pygame.Rect:
    """
    Draw a panel that perfectly fits the given text with automatic sizing.

    Args:
        screen: Surface to draw on
        lines: Text to display (string or list of strings)
        font: Font to use for rendering
        theme: Theme object with colors and spacing
        x: X position (None for centered horizontally)
        y: Y position (None for centered vertically)
        padding: Internal padding (defaults to theme.spacing(2))
        line_spacing: Space between lines (defaults to theme.spacing(1))
        text_color: Color for text (defaults to theme.colors["text"])
        align: Text alignment within panel ("left", "center", "right")
        width: Fixed panel width (overrides measured width when set)
        max_width: Maximum width for the panel (for wrapping)
        auto_wrap: If True, automatically wrap long lines to fit max_width
        min_height: Minimum height for the panel

    Returns:
        The rect of the panel that was drawn
    """
    if isinstance(lines, str):
        lines = [lines]

    if padding is None:
        padding = theme.spacing(2)
    if line_spacing is None:
        line_spacing = theme.spacing(1)
    if text_color is None:
        text_color = theme.colors["text"]

    effective_max_width = max_width if max_width is not None else width

    if auto_wrap and effective_max_width:
        max_text_width = effective_max_width - padding * 2
        wrapped_lines = []
        for line in lines:
            if line == "":
                wrapped_lines.append("")
            else:
                wrapped_lines.extend(wrap_text_lines(line, font, max_text_width))
        lines = wrapped_lines

    text_width, text_height = measure_text_block(lines, font, line_spacing)

    computed_height = max(text_height + padding * 2, min_height or 0)

    if width is not None:
        computed_width = width
    else:
        computed_width = text_width + padding * 2
        if max_width:
            computed_width = min(computed_width, max_width)

    if x is None:
        x = (screen.get_width() - computed_width) // 2
    if y is None:
        y = (screen.get_height() - computed_height) // 2

    panel_rect = pygame.Rect(x, y, computed_width, computed_height)
    draw_panel(screen, panel_rect, theme, draw_border=draw_border)

    current_y = y + padding
    for line in lines:
        text_surface = font.render(line, True, text_color)

        if align == "center":
            text_x = x + (computed_width - text_surface.get_width()) // 2
        elif align == "left":
            text_x = x + padding
        else:
            text_x = x + computed_width - padding - text_surface.get_width()

        screen.blit(text_surface, (text_x, current_y))
        current_y += text_surface.get_height() + line_spacing

    return panel_rect


def draw_paginated_panel(
    screen: pygame.Surface,
    rect: pygame.Rect | Tuple[int, int, int, int],
    theme: Theme,
    font: pygame.font.Font,
    paged_state: PagedTextState,
    padding: Optional[int] = None,
    line_spacing: Optional[int] = None,
    prompt_text: Optional[str] = None,
) -> pygame.Rect:
    if padding is None:
        padding = theme.spacing(2)
    if line_spacing is None:
        line_spacing = theme.spacing(1)

    base_rect = pygame.Rect(rect)
    draw_panel(screen, base_rect, theme, draw_border=True)

    visible_lines = paged_state.current_page_lines()
    text_y = base_rect.y + padding
    line_height = font.get_linesize()

    for index, line in enumerate(visible_lines):
        surf = font.render(line, True, theme.colors["text"])
        text_x = base_rect.x + padding
        screen.blit(surf, (text_x, text_y))
        if index < len(visible_lines) - 1:
            text_y += line_height + line_spacing

    cue = "" if paged_state.is_last_page else "..."
    cue_surf = font.render(cue, True, theme.colors["text_hint"])
    cue_x = base_rect.right - padding - cue_surf.get_width()
    cue_y = base_rect.bottom - padding - cue_surf.get_height()
    screen.blit(cue_surf, (cue_x, cue_y))

    if prompt_text:
        prompt_surf = font.render(prompt_text, True, theme.colors["text_hint"])
        prompt_pos = prompt_surf.get_rect(
            center=(screen.get_width() // 2, base_rect.bottom + padding)
        )
        screen.blit(prompt_surf, prompt_pos)

    return base_rect


def draw_selection_panel(
    screen: pygame.Surface,
    options: List[str],
    selected_index: int,
    font: pygame.font.Font,
    theme: Theme,
    x: Optional[int] = None,
    y: Optional[int] = None,
    padding: Optional[int] = None,
    option_spacing: Optional[int] = None,
    width: Optional[int] = None,
    align: str = "center",
    arrow_size: Optional[int] = None,
    draw_border: bool = True,
) -> pygame.Rect:
    """
    Render a choice list inside a styled panel and highlight the selected option.

    Args:
        screen: Surface to draw on.
        options: Labels for each option.
        selected_index: Zero-based index of the active option.
        font: Font used for option labels.
        theme: Theme providing colors and spacing.
        x: Left position of the panel (centered when None).
        y: Top position of the panel (centered when None).
        padding: Inner padding in pixels.
        option_spacing: Vertical spacing between options.
        width: Desired panel width; grows if content needs more space.
        align: Horizontal alignment of text within the panel.
        arrow_size: Size of the selection arrow.

    Returns:
        The rect of the drawn panel.
    """
    if padding is None:
        padding = theme.spacing(2)
    if option_spacing is None:
        option_spacing = theme.spacing(3)
    if arrow_size is None:
        arrow_size = theme.spacing(1)

    text_heights = [font.get_linesize() for _ in options]
    text_widths = [font.size(option)[0] for option in options]
    widest_text = max(text_widths) if text_widths else 0

    arrow_space = theme.spacing(2) + arrow_size
    min_panel_width = widest_text + padding * 2 + arrow_space
    resolved_width = max(width, min_panel_width) if width else min_panel_width

    total_height = sum(text_heights)
    total_height += option_spacing * (len(options) - 1) if options else 0
    resolved_height = total_height + padding * 2

    if x is None:
        x = (screen.get_width() - resolved_width) // 2
    if y is None:
        y = (screen.get_height() - resolved_height) // 2

    panel_rect = pygame.Rect(x, y, resolved_width, resolved_height)
    draw_panel(screen, panel_rect, theme, draw_border=draw_border)

    current_y = y + padding
    for index, option in enumerate(options):
        is_selected = index == selected_index
        color = theme.colors["text_selected"] if is_selected else theme.colors["text"]
        text_surface = font.render(option, False, color)
        if align == "left":
            text_x = x + padding + arrow_space
        elif align == "right":
            text_x = x + resolved_width - padding - text_surface.get_width()
        else:
            text_x = x + (resolved_width - text_surface.get_width()) // 2

        screen.blit(text_surface, (text_x, current_y))

        if is_selected:
            arrow_x = text_x - theme.spacing(1)
            arrow_y = current_y + text_surface.get_height() // 2
            points = [
                (arrow_x, arrow_y),
                (arrow_x - arrow_size, arrow_y - arrow_size // 2),
                (arrow_x - arrow_size, arrow_y + arrow_size // 2),
            ]
            pygame.draw.polygon(screen, color, points)

        current_y += text_surface.get_height() + option_spacing

    return panel_rect


def cursor_suffix(time_ms: int, interval_ms: int = 400) -> str:
    return "|" if (time_ms // interval_ms) % 2 == 0 else ""


def draw_blinking_cursor(
    screen: pygame.Surface,
    x: int,
    y: int,
    height: int,
    theme,
    time_ms: int,
    interval_ms: int = 400,
):
    if (time_ms // interval_ms) % 2 == 0:
        width = max(3, height // 8)
        cursor_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, theme.colors["text_selected"], cursor_rect)


def draw_input_panel(
    screen: pygame.Surface,
    current_text: str,
    font: pygame.font.Font,
    theme: Theme,
    x: Optional[int] = None,
    y: Optional[int] = None,
    width: Optional[int] = None,
    padding: Optional[int] = None,
    template: Optional[str] = None,
    text_color: Optional[Tuple[int, int, int]] = None,
    template_color: Optional[Tuple[int, int, int]] = None,
    show_cursor: bool = True,
    time_ms: Optional[int] = None,
    cursor_interval_ms: int = 400,
    draw_border: bool = True,
) -> pygame.Rect:
    """
    Draw a single-line input panel with optional placeholder template and cursor.

    Args:
        screen: Surface to draw on.
        current_text: Text the player has entered so far.
        font: Font for rendering text.
        theme: Theme providing colors and spacing.
        x: Left position of the panel (centered when None).
        y: Top position of the panel (centered when None).
        width: Desired width; grows to fit content when smaller.
        padding: Inner padding in pixels.
        template: Placeholder string that reveals characters as the user types.
        text_color: Color for typed characters.
        template_color: Color for remaining template characters.
        show_cursor: Whether to render a blinking cursor.
        time_ms: Current time in milliseconds for cursor animation.
        cursor_interval_ms: Blink speed in milliseconds.
        draw_border: Whether to render the decorative border.

    Returns:
        Rect of the drawn panel.
    """
    if padding is None:
        padding = theme.spacing(2)
    if text_color is None:
        text_color = theme.colors["text_selected"]
    if template_color is None:
        template_color = theme.colors["text_hint"]

    visible_template = template or ""
    template_chars = list(visible_template)
    for idx, char in enumerate(current_text):
        if idx < len(template_chars):
            template_chars[idx] = char
        else:
            template_chars.append(char)
    display_text = "".join(template_chars) if visible_template else current_text

    base_surface = font.render(display_text, True, template_color)

    measured_width = base_surface.get_width() + padding * 2
    measured_height = base_surface.get_height() + padding * 2
    resolved_width = width or measured_width
    resolved_height = measured_height

    if x is None:
        x = (screen.get_width() - resolved_width) // 2
    if y is None:
        y = (screen.get_height() - resolved_height) // 2

    panel_rect = pygame.Rect(x, y, resolved_width, resolved_height)
    draw_panel(screen, panel_rect, theme, draw_border=draw_border)

    text_x = x + padding
    text_y = y + padding

    if visible_template:
        filled_text = "".join(template_chars[: len(current_text)])
    else:
        filled_text = current_text

    filled_width = font.size(filled_text)[0]

    available_text_width = resolved_width - padding * 2
    filled_surface = font.render(filled_text, True, text_color)
    scroll_offset = max(filled_surface.get_width() - available_text_width, 0)

    base_area = pygame.Rect(
        scroll_offset, 0, available_text_width, base_surface.get_height()
    )
    filled_area = pygame.Rect(
        scroll_offset, 0, available_text_width, filled_surface.get_height()
    )

    screen.blit(base_surface, (text_x, text_y), area=base_area)
    screen.blit(filled_surface, (text_x, text_y), area=filled_area)

    if show_cursor and time_ms is not None:
        cursor_x = text_x + min(filled_width, available_text_width)
        cursor_y = text_y
        draw_blinking_cursor(
            screen,
            cursor_x,
            cursor_y,
            filled_surface.get_height(),
            theme,
            time_ms,
            interval_ms=cursor_interval_ms,
        )

    return panel_rect
