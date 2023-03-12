import esper

from asteroids.ecs.entities import (
    create_player_ship,
    create_spawner,
    create_scoreboard,
    create_player_input,
)
from asteroids.ecs.systems import add_systems


def build_world() -> esper.World:
    world = esper.World()

    # initialize systems
    add_systems(world)

    # add entities
    create_scoreboard(world)

    create_spawner(world)

    create_player_ship(world)

    create_player_input(world)

    return world
