import math

from .components import Collidable, Position, Velocity
from .enums import CollidableKind


def calculate_distance(pos1: Position, pos2: Position) -> float:
    delta_x = pos2.x - pos1.x
    delta_y = pos2.y - pos1.y

    return math.sqrt(delta_x**2 + delta_y**2)


def calculate_velocity(
    start: Position, end: Position, *, magnitude: float = 1.0
) -> Velocity:
    delta_x = end.x - start.x
    delta_y = end.y - start.y

    norm = math.sqrt(delta_x**2 + delta_y**2)

    return Velocity(x=magnitude * delta_x / norm, y=magnitude * delta_y / norm)


def check_collision(
    pos1: Position, collidable1: Collidable, pos2: Position, collidable2: Collidable
) -> bool:
    if (
        collidable1.kind == CollidableKind.Circle
        and collidable2.kind == CollidableKind.Circle
    ):
        return check_circle_collision(
            pos1, collidable1.radius, pos2, collidable2.radius
        )

    raise NotImplementedError("Collision check not implemented")


def check_circle_collision(
    pos1: Position, radius1: float, pos2: Position, radius2: float
) -> bool:
    delta_x = pos2.x - pos1.x
    delta_y = pos2.y - pos1.y

    distance = math.sqrt(delta_x**2 + delta_y**2)

    return distance < (radius1 + radius2)
