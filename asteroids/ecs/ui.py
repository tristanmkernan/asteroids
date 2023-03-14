import pygame

from .components import Position, Renderable
from .enums import RenderableKind
from .utils import apply_rotation_to_offset


def render(screen: pygame.Surface, renderable: Renderable, position: Position):
    render_position = position

    if renderable.offset:
        offset_rotated = apply_rotation_to_offset(
            renderable.offset, render_position.rotation
        )

        render_position = Position(
            x=render_position.x + offset_rotated.x,
            y=render_position.y + offset_rotated.y,
        )

    match renderable.kind:
        case RenderableKind.Circle:
            pygame.draw.circle(
                screen, renderable.color, render_position.tuple, renderable.radius
            )
        case RenderableKind.Triangle:
            pass
