import logging
import random

import esper


from asteroids.constants import SCREEN_HEIGHT, SCREEN_WIDTH

from .components import (
    Acceleration,
    Asteroid,
    Bullet,
    Collidable,
    PlayerKeyInput,
    Position,
    Rotation,
    ScoreTracker,
    Velocity,
    Spawning,
    Renderable,
    PlayerShip,
)
from .enums import CollidableKind, RenderableKind, ScoreEventKind
from .utils import calculate_velocity


logger = logging.getLogger(__name__)


def create_scoreboard(world: esper.World):
    scoreboard = world.create_entity()

    world.add_component(scoreboard, ScoreTracker())


def create_spawner(world: esper.World):
    spawner = world.create_entity()

    world.add_component(spawner, Spawning(rate=1.0 / 1_000))

    return spawner


def spawn_asteroid(world: esper.World):
    asteroid = world.create_entity()

    radius = random.randrange(10, 30)

    # TODO
    # random spawn point

    # random velocity

    world.add_component(asteroid, Asteroid())
    world.add_component(asteroid, Velocity(x=0, y=0))
    world.add_component(asteroid, Position(x=spawn_pos.x, y=spawn_pos.y))
    world.add_component(asteroid, Renderable(radius=radius))
    world.add_component(asteroid, Collidable(radius=radius, kind=CollidableKind.Circle))

    return asteroid


def create_player_ship(world: esper.World):
    player_ship = world.create_entity()

    world.add_component(player_ship, PlayerShip())
    world.add_component(player_ship, Position(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2))
    world.add_component(player_ship, Velocity())
    world.add_component(player_ship, Acceleration())
    world.add_component(player_ship, Renderable(RenderableKind.Circle, radius=15, color=(255, 0, 0)))
    world.add_component(player_ship, Collidable(kind=CollidableKind.Circle, radius=3, ))



# TODO turret -> ship
def create_bullet(world: esper.World, player_ship):
    bullet = world.create_entity()

    # TODO math
    player_pos = world.component_for_entity(player_ship, Position)
    player_rotation = world.component_for_entity(player_ship, Rotation)

    velocity = calculate_velocity(player_pos, player_rotation, magnitude=0.75)

    world.add_component(bullet, Position(x=turret_pos.x, y=turret_pos.y))
    world.add_component(bullet, velocity)
    world.add_component(bullet, Renderable(radius=3, color=(0, 0, 0)))
    world.add_component(bullet, Collidable(radius=3, kind=CollidableKind.Circle))
    world.add_component(bullet, Bullet())

    return bullet


def create_player_input(world: esper.World):
    player_input = world.create_entity()

    world.add_component(player_input, PlayerKeyInput())


def track_score_event(world: esper.World, kind: ScoreEventKind):
    _, score_tracker = world.get_component(ScoreTracker)[0]

    score_tracker.recent_events.insert(0, kind)
    score_tracker.recent_events = score_tracker.recent_events[:10]

    score_tracker.scores[kind] += 1


# TODO could be part of difficulty increase over time
def increase_spawn_rate(world: esper.World, multiplier: float = 1.25):
    for _, spawning in world.get_component(Spawning):
        spawning.rate *= multiplier


def set_player_accelerating(world: esper.World, val: bool):
    _, (_, acc) = world.get_components(PlayerShip, Acceleration)[0]

    if val:
        # TODO
        pass
    else:
        acc.x = acc.y = 0.0


def set_player_decelerating(world: esper.World, val: bool):
    _, (_, acc) = world.get_components(PlayerShip, Acceleration)[0]

    if val:
        # TODO
        pass
    else:
        acc.x = acc.y = 0.0
