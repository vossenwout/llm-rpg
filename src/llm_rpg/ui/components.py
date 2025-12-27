from dataclasses import dataclass
import pygame
from typing import Tuple, List, Optional
from llm_rpg.utils.theme import Theme

PANEL_BORDER_TILE_SIZE = 8


def _first_opaque_x(surface: pygame.Surface, y: int, tile_size: int) -> int:
    for x in range(tile_size):
        if surface.get_at((x, y)).a > 0:
            return x
    return tile_size


def _last_opaque_x(surface: pygame.Surface, y: int, tile_size: int) -> int:
    for x in range(tile_size - 1, -1, -1):
        if surface.get_at((x, y)).a > 0:
            return x
    return -1


def _get_corner_cutoffs(
    border_surface: pygame.Surface, tile_size: int
) -> tuple[list[int], list[int], list[int], list[int]]:
    tiles = _get_nine_slice_tiles(border_surface, tile_size)
    top_left, _, top_right, _, _, _, bottom_left, _, bottom_right = tiles

    top_left_cut = [_first_opaque_x(top_left, y, tile_size) for y in range(tile_size)]
    top_right_cut = [_last_opaque_x(top_right, y, tile_size) for y in range(tile_size)]
    bottom_left_cut = [
        _first_opaque_x(bottom_left, y, tile_size) for y in range(tile_size)
    ]
    bottom_right_cut = [
        _last_opaque_x(bottom_right, y, tile_size) for y in range(tile_size)
    ]

    return (
        top_left_cut,
        top_right_cut,
        bottom_left_cut,
        bottom_right_cut,
    )


def _apply_corner_cutouts(
    surface: pygame.Surface,
    cutoffs: tuple[list[int], list[int], list[int], list[int]],
    tile_size: int,
) -> None:
    width, height = surface.get_size()
    top_left_cut, top_right_cut, bottom_left_cut, bottom_right_cut = cutoffs
    right_x0 = width - tile_size
    bottom_y0 = height - tile_size

    for y in range(tile_size):
        tl_cut = top_left_cut[y]
        for x in range(tl_cut):
            surface.set_at((x, y), (0, 0, 0, 0))

        tr_cut = top_right_cut[y]
        if tr_cut == -1:
            start = right_x0
        else:
            start = right_x0 + tr_cut + 1
        for x in range(start, right_x0 + tile_size):
            surface.set_at((x, y), (0, 0, 0, 0))

        bl_cut = bottom_left_cut[y]
        for x in range(bl_cut):
            surface.set_at((x, bottom_y0 + y), (0, 0, 0, 0))

        br_cut = bottom_right_cut[y]
        if br_cut == -1:
            start = right_x0
        else:
            start = right_x0 + br_cut + 1
        for x in range(start, right_x0 + tile_size):
            surface.set_at((x, bottom_y0 + y), (0, 0, 0, 0))


def _get_nine_slice_tiles(
    surface: pygame.Surface, tile_size: int
) -> tuple[pygame.Surface, ...]:
    tiles = []
    for row in range(3):
        for col in range(3):
            rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
            tiles.append(surface.subsurface(rect))
    return tuple(tiles)


def _blit_tiled_horizontal(
    screen: pygame.Surface,
    tile: pygame.Surface,
    x: int,
    y: int,
    width: int,
) -> None:
    tile_w = tile.get_width()
    tile_h = tile.get_height()
    end_x = x + width
    current_x = x
    while current_x < end_x:
        remaining = end_x - current_x
        if remaining >= tile_w:
            screen.blit(tile, (current_x, y))
        else:
            screen.blit(tile, (current_x, y), area=pygame.Rect(0, 0, remaining, tile_h))
        current_x += tile_w


def _blit_tiled_vertical(
    screen: pygame.Surface,
    tile: pygame.Surface,
    x: int,
    y: int,
    height: int,
) -> None:
    tile_w = tile.get_width()
    tile_h = tile.get_height()
    end_y = y + height
    current_y = y
    while current_y < end_y:
        remaining = end_y - current_y
        if remaining >= tile_h:
            screen.blit(tile, (x, current_y))
        else:
            screen.blit(tile, (x, current_y), area=pygame.Rect(0, 0, tile_w, remaining))
        current_y += tile_h


def _draw_nine_slice_panel(
    screen: pygame.Surface,
    rect: pygame.Rect,
    border_surface: pygame.Surface,
    tile_size: int,
    fill_color: Tuple[int, int, int],
) -> None:
    tiles = _get_nine_slice_tiles(border_surface, tile_size)
    top_left, top, top_right, left, _, right, bottom_left, bottom, bottom_right = tiles

    fill_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    fill_surface.fill(fill_color)
    cutoffs = _get_corner_cutoffs(border_surface, tile_size)
    _apply_corner_cutouts(fill_surface, cutoffs, tile_size)
    screen.blit(fill_surface, rect.topleft)

    screen.blit(top_left, rect.topleft)
    screen.blit(top_right, (rect.right - tile_size, rect.top))
    screen.blit(bottom_left, (rect.left, rect.bottom - tile_size))
    screen.blit(bottom_right, (rect.right - tile_size, rect.bottom - tile_size))

    edge_width = rect.width - tile_size * 2
    edge_height = rect.height - tile_size * 2
    if edge_width > 0:
        _blit_tiled_horizontal(screen, top, rect.left + tile_size, rect.top, edge_width)
        _blit_tiled_horizontal(
            screen,
            bottom,
            rect.left + tile_size,
            rect.bottom - tile_size,
            edge_width,
        )
    if edge_height > 0:
        _blit_tiled_vertical(screen, left, rect.left, rect.top + tile_size, edge_height)
        _blit_tiled_vertical(
            screen,
            right,
            rect.right - tile_size,
            rect.top + tile_size,
            edge_height,
        )


def draw_checkerboard_background(screen: pygame.Surface, theme: Theme) -> None:
    tile = theme.checkerboard_background
    tile_width = tile.get_width()
    tile_height = tile.get_height()
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    for y in range(0, screen_height, tile_height):
        for x in range(0, screen_width, tile_width):
            screen.blit(tile, (x, y))


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
    if draw_border:
        if pygame.display.get_surface() is not None and not getattr(
            theme, "panel_border_converted", False
        ):
            theme.panel_border = theme.panel_border.convert_alpha()
            theme.panel_border_converted = True
        tile_size = PANEL_BORDER_TILE_SIZE
        if base_rect.width >= tile_size * 2 and base_rect.height >= tile_size * 2:
            _draw_nine_slice_panel(
                screen,
                base_rect,
                theme.panel_border,
                tile_size,
                theme.colors["panel_inner"],
            )
            return

    if draw_border:
        outer_thickness = 2
        inner_thickness = 1
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


def render_text_with_shadow(
    font: pygame.font.Font,
    text: str,
    color: Tuple[int, int, int],
    shadow_color: Tuple[int, int, int, int],
    shadow_offset: Tuple[int, int] = (1, 1),
    antialias: bool = True,
) -> pygame.Surface:
    base_surface = font.render(text, antialias, color)
    shadow_surface = font.render(text, antialias, shadow_color[:3])
    shadow_surface.set_alpha(shadow_color[3])
    width = max(base_surface.get_width(), shadow_surface.get_width() + shadow_offset[0])
    height = max(
        base_surface.get_height(), shadow_surface.get_height() + shadow_offset[1]
    )
    combined = pygame.Surface((width, height), pygame.SRCALPHA)
    combined.blit(shadow_surface, shadow_offset)
    combined.blit(base_surface, (0, 0))
    return combined


def draw_hud_backdrop(
    screen: pygame.Surface,
    rect: pygame.Rect | Tuple[int, int, int, int],
    theme: Theme,
    draw_border: bool = True,
) -> pygame.Rect:
    base_rect = pygame.Rect(rect)
    backdrop = pygame.Surface(base_rect.size, pygame.SRCALPHA)
    backdrop.fill(theme.colors["hud_backdrop"])
    if draw_border:
        pygame.draw.rect(backdrop, theme.colors["hud_border"], backdrop.get_rect(), 1)
    screen.blit(backdrop, base_rect.topleft)
    return base_rect


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
    cue_surf = render_text_with_shadow(
        font=font,
        text=cue,
        color=theme.colors["text_hint"],
        shadow_color=theme.colors["text_hint_shadow"],
    )
    cue_x = base_rect.right - padding - cue_surf.get_width()
    cue_y = base_rect.bottom - padding - cue_surf.get_height()
    screen.blit(cue_surf, (cue_x, cue_y))

    if prompt_text:
        prompt_surf = render_text_with_shadow(
            font=font,
            text=prompt_text,
            color=theme.colors["text_hint"],
            shadow_color=theme.colors["text_hint_shadow"],
        )
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
    max_width: Optional[int] = None,
    auto_wrap: bool = False,
    line_spacing: Optional[int] = None,
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
        max_width: Optional maximum width for the panel when auto wrapping.
        auto_wrap: Wrap option text to fit within the panel.
        line_spacing: Spacing between wrapped lines.

    Returns:
        The rect of the drawn panel.
    """
    if padding is None:
        padding = theme.spacing(2)
    if option_spacing is None:
        option_spacing = theme.spacing(3)
    if arrow_size is None:
        arrow_size = theme.spacing(1)
    if line_spacing is None:
        line_spacing = theme.spacing(1)

    arrow_space = theme.spacing(2) + arrow_size

    if auto_wrap:
        available_wrap_width = None
        if width:
            available_wrap_width = width - padding * 2 - arrow_space
        elif max_width:
            available_wrap_width = max_width - padding * 2 - arrow_space
        else:
            available_wrap_width = screen.get_width() - padding * 2 - arrow_space

        wrapped_options: List[List[str]] = [
            wrap_text_lines(option, font, available_wrap_width) for option in options
        ]
    else:
        wrapped_options = [[option] for option in options]

    block_sizes = [
        measure_text_block(lines, font, line_spacing=line_spacing)
        for lines in wrapped_options
    ]
    widest_text = max((size[0] for size in block_sizes), default=0)
    min_panel_width = widest_text + padding * 2 + arrow_space

    resolved_width = max(width, min_panel_width) if width else min_panel_width
    if max_width:
        resolved_width = (
            min(resolved_width, max_width)
            if max_width >= min_panel_width
            else min_panel_width
        )

    total_height = sum(size[1] for size in block_sizes)
    total_height += (
        option_spacing * (len(wrapped_options) - 1) if wrapped_options else 0
    )
    resolved_height = total_height + padding * 2

    if x is None:
        x = (screen.get_width() - resolved_width) // 2
    if y is None:
        y = (screen.get_height() - resolved_height) // 2

    panel_rect = pygame.Rect(x, y, resolved_width, resolved_height)
    draw_panel(screen, panel_rect, theme, draw_border=draw_border)

    current_y = y + padding
    for index, lines in enumerate(wrapped_options):
        is_selected = index == selected_index
        color = theme.colors["text_selected"] if is_selected else theme.colors["text"]
        show_indicator = (pygame.time.get_ticks() // 400) % 2 == 0
        option_top = current_y
        option_height = block_sizes[index][1] if index < len(block_sizes) else 0

        for line_idx, line in enumerate(lines):
            text_surface = font.render(line, False, color)
            if align == "left":
                text_x = x + padding + arrow_space
            elif align == "right":
                text_x = x + resolved_width - padding - text_surface.get_width()
            else:
                text_x = x + (resolved_width - text_surface.get_width()) // 2

            screen.blit(text_surface, (text_x, current_y))

            if is_selected and line_idx == 0 and show_indicator:
                arrow_x = text_x - theme.spacing(1)
                arrow_y = option_top + option_height // 2
                points = [
                    (arrow_x, arrow_y),
                    (arrow_x - arrow_size, arrow_y - arrow_size // 2),
                    (arrow_x - arrow_size, arrow_y + arrow_size // 2),
                ]
                pygame.draw.polygon(screen, color, points)

            current_y += text_surface.get_height()
            if line_idx < len(lines) - 1:
                current_y += line_spacing

        if index < len(wrapped_options) - 1:
            current_y += option_spacing

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
    has_template = len(visible_template) > 0

    if has_template:
        width_chars = (
            visible_template
            + current_text
            + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        )
        cell_width = max(font.size(char)[0] for char in width_chars) or 1
        text_height = font.get_height()
        total_cells = max(len(visible_template), len(current_text))

        template_cells = len(visible_template)
        measured_width = cell_width * max(template_cells, total_cells) + padding * 2
        measured_height = text_height + padding * 2
        if width is None:
            resolved_width = measured_width
        else:
            resolved_width = max(width, measured_width)
        resolved_height = measured_height

        if x is None:
            x = (screen.get_width() - resolved_width) // 2
        if y is None:
            y = (screen.get_height() - resolved_height) // 2

        panel_rect = pygame.Rect(x, y, resolved_width, resolved_height)
        draw_panel(screen, panel_rect, theme, draw_border=draw_border)

        text_x = x + padding
        text_y = y + padding
        available_text_width = resolved_width - padding * 2
        visible_cells = max(1, available_text_width // cell_width)
        visible_cells = min(visible_cells, max(template_cells, total_cells))
        start_index = 0
        end_index = min(max(template_cells, total_cells), start_index + visible_cells)

        cursor_index = (
            len(current_text)
            if show_cursor
            and time_ms is not None
            and len(current_text) < template_cells
            else -1
        )
        for idx in range(start_index, end_index):
            slot_x = text_x + (idx - start_index) * cell_width
            if idx == cursor_index:
                pass
            elif idx >= len(current_text):
                template_char = (
                    visible_template[idx] if idx < len(visible_template) else " "
                )
                template_surface = font.render(template_char, True, template_color)
                template_x = slot_x + (cell_width - template_surface.get_width()) // 2
                screen.blit(template_surface, (template_x, text_y))
            else:
                typed_char = current_text[idx]
                typed_surface = font.render(typed_char, True, text_color)
                typed_x = slot_x + (cell_width - typed_surface.get_width()) // 2
                screen.blit(typed_surface, (typed_x, text_y))

        if show_cursor and time_ms is not None and len(current_text) < template_cells:
            cursor_slot = min(len(current_text), start_index + visible_cells)
            cursor_width = max(3, text_height // 8)
            cursor_x = (
                text_x
                + (cursor_slot - start_index) * cell_width
                + (cell_width - cursor_width) // 2
            )
            draw_blinking_cursor(
                screen,
                cursor_x,
                text_y,
                text_height,
                theme,
                time_ms,
                interval_ms=cursor_interval_ms,
            )

        return panel_rect

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
