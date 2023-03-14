import logging
import random

import esper


from asteroids.constants import SCREEN_HEIGHT, SCREEN_WIDTH

from .components import (
    Acceleration,
    Asteroid,
    Bullet,
    BulletAmmo,
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

    world.add_component(spawner, Spawning(rate=1.0 / 3_000))

    return spawner


def spawn_asteroid(world: esper.World):
    asteroid = world.create_entity()

    radius = random.randrange(10, 30)

    # TODO
    # random spawn point
    position = Position(x=random.randrange(50, SCREEN_WIDTH - 50), y=0)

    velocity = Velocity(x=(random.random() - 0.5) / 50, y=random.random() / 50)

    # random velocity

    world.add_component(asteroid, Asteroid())
    world.add_component(asteroid, velocity)
    world.add_component(asteroid, position)
    world.add_component(asteroid, Renderable(kind=RenderableKind.Circle, radius=radius))
    world.add_component(asteroid, Collidable(radius=radius, kind=CollidableKind.Circle))

    return asteroid


def create_player_ship(world: esper.World):
    player_ship = world.create_entity()

    world.add_component(player_ship, PlayerShip())
    world.add_component(player_ship, Position(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2))
    world.add_component(player_ship, Velocity(max=0.25))
    world.add_component(player_ship, Acceleration())
    world.add_component(
        player_ship, Renderable(RenderableKind.Circle, radius=15, color=(255, 0, 0))
    )
    world.add_component(
        player_ship,
        Collidable(
            kind=CollidableKind.Circle,
            radius=3,
        ),
    )
    world.add_component(player_ship, Rotation())
    world.add_component(
        player_ship, BulletAmmo(recharge_rate=1.0 / 500.0, count=3, max=5)
    )


def create_bullet(world: esper.World):
    player, (
        player_ship,
        player_position,
        player_rotation,
        player_velocity,
        bullet_ammo,
    ) = world.get_components(PlayerShip, Position, Rotation, Velocity, BulletAmmo)[0]

    if bullet_ammo.empty:
        return

    # subtract one bullet
    bullet_ammo.count -= 1

    bullet = world.create_entity()

    # sneaky math: copy player velocity but change magnitude
    # FIXME TODO this doesnt work if the player isnt moving!!!
    # need to use position and rotation
    # also shoots backwards when moving backwards even if facing forward lol
    velocity = Velocity(x=player_velocity.x, y=player_velocity.y, max=0.75)
    velocity.maximize()

    world.add_component(bullet, Position(x=player_position.x, y=player_position.y))
    world.add_component(bullet, velocity)
    world.add_component(
        bullet, Renderable(kind=RenderableKind.Circle, radius=3, color=(0, 0, 0))
    )
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
    _, (_, acc, rot) = world.get_components(PlayerShip, Acceleration, Rotation)[0]

    if val:
        # TODO
        acc.x = acc.y = 1.0 / 2_000.0
    else:
        acc.x = acc.y = 0.0


def set_player_decelerating(world: esper.World, val: bool):
    _, (_, acc, rot) = world.get_components(PlayerShip, Acceleration, Rotation)[0]

    if val:
        # TODO
        acc.x = acc.y = -1.0 / 2_000.0
    else:
        acc.x = acc.y = 0.0
