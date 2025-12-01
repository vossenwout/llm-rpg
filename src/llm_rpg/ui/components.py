import pygame
from typing import Tuple


def draw_panel(
    screen: pygame.Surface, rect: pygame.Rect | Tuple[int, int, int, int], theme
):
    base_rect = pygame.Rect(rect)
    outer_thickness = max(2, theme.scale)
    inner_thickness = max(2, theme.scale - 1)

    pygame.draw.rect(screen, theme.colors["border_light"], base_rect, outer_thickness)

    inner_rect = base_rect.inflate(-outer_thickness * 2, -outer_thickness * 2)
    pygame.draw.rect(screen, theme.colors["border_dark"], inner_rect, inner_thickness)

    fill_rect = inner_rect.inflate(-inner_thickness * 2, -inner_thickness * 2)
    pygame.draw.rect(screen, theme.colors["panel_inner"], fill_rect)


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
