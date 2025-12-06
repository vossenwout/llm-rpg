import pygame
from typing import Tuple, List, Optional
from llm_rpg.utils.theme import Theme


def draw_panel(
    screen: pygame.Surface, rect: pygame.Rect | Tuple[int, int, int, int], theme
):
    base_rect = pygame.Rect(rect)
    outer_thickness = 2
    inner_thickness = 1

    pygame.draw.rect(screen, theme.colors["border_light"], base_rect, outer_thickness)

    inner_rect = base_rect.inflate(-outer_thickness * 2, -outer_thickness * 2)
    pygame.draw.rect(screen, theme.colors["border_dark"], inner_rect, inner_thickness)

    fill_rect = inner_rect.inflate(-inner_thickness * 2, -inner_thickness * 2)
    pygame.draw.rect(screen, theme.colors["panel_inner"], fill_rect)


def wrap_text_lines(
    text: str,
    font: pygame.font.Font,
    max_width: int,
    max_lines: int | None = None,
) -> List[str]:
    words = text.split()
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
    max_width: Optional[int] = None,
    auto_wrap: bool = False,
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
        max_width: Maximum width for the panel (for wrapping)
        auto_wrap: If True, automatically wrap long lines to fit max_width

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

    if auto_wrap and max_width:
        max_text_width = max_width - padding * 2
        wrapped_lines = []
        for line in lines:
            wrapped_lines.extend(wrap_text_lines(line, font, max_text_width))
        lines = wrapped_lines

    text_width, text_height = measure_text_block(lines, font, line_spacing)

    panel_width = text_width + padding * 2
    panel_height = text_height + padding * 2

    if max_width:
        panel_width = min(panel_width, max_width)

    if x is None:
        x = (screen.get_width() - panel_width) // 2
    if y is None:
        y = (screen.get_height() - panel_height) // 2

    panel_rect = pygame.Rect(x, y, panel_width, panel_height)
    draw_panel(screen, panel_rect, theme)

    current_y = y + padding
    for line in lines:
        text_surface = font.render(line, True, text_color)

        if align == "center":
            text_x = x + (panel_width - text_surface.get_width()) // 2
        elif align == "left":
            text_x = x + padding
        else:
            text_x = x + panel_width - padding - text_surface.get_width()

        screen.blit(text_surface, (text_x, current_y))
        current_y += text_surface.get_height() + line_spacing

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
