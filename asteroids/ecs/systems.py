import logging
import random

import esper
import pygame
import pygame.constants

from asteroids.constants import SCREEN_HEIGHT, SCREEN_WIDTH


from .components import (
    Bullet,
    Collidable,
    PlayerKeyInput,
    Position,
    Velocity,
    Spawning,
    Renderable,
    ScoreTracker,
)
from .entities import (
    create_bullet,
    set_player_accelerating,
    set_player_decelerating,
    track_score_event,
)
from .enums import RenderableKind, ScoreEventKind, InputEventKind, PlayerActionKind
from .utils import calculate_distance, calculate_velocity, check_collision


logger = logging.getLogger(__name__)


def add_systems(world: esper.World):
    world.add_processor(MovementProcessor())
    world.add_processor(RenderingProcessor())
    world.add_processor(SpawningProcessor())
    world.add_processor(BulletProcessor())
    world.add_processor(PlayerInputProcessor())
    world.add_processor(ScoreTimeTrackerProcessor())


class MovementProcessor(esper.Processor):
    def process(self, *args, delta, **kwargs):
        for ent, (vel, pos) in self.world.get_components(Velocity, Position):
            pos.x += vel.x * delta
            pos.y += vel.y * delta


class SpawningProcessor(esper.Processor):
    def process(self, *args, delta, **kwargs):
        for ent, (spawning, pos) in self.world.get_components(Spawning, Position):
            spawning.elapsed += delta

            if spawning.elapsed > spawning.every:
                # duplicate spawn position
                enemy = spawn_enemy(self.world, ent)

                logger.info("Spawned new entity id=%d", enemy)

                track_score_event(self.world, ScoreEventKind.EnemySpawn)

                spawning.elapsed = 0


class RenderingProcessor(esper.Processor):
    def __init__(self) -> None:
        super().__init__()

        self.font = pygame.font.SysFont("Comic", 40)

    def process(self, *args, **kwargs):
        show_fps = kwargs["show_fps"]
        screen = kwargs["screen"]
        clock = kwargs["clock"]

        screen.fill((255, 255, 255))

        for ent, (disp, pos) in self.world.get_components(Renderable, Position):
            match disp.kind:
                case RenderableKind.Circle:
                    pygame.draw.circle(screen, disp.color, pos.tuple, disp.radius)
                case RenderableKind.Triangle:
                    # TODO
                    pygame.draw.polygon(screen, disp.color, [])

        scoreboard, score_tracker = self.world.get_component(ScoreTracker)[0]

        time_str = f"Time {score_tracker.scores[ScoreEventKind.Time]:.1f}"
        screen.blit(
            self.font.render(time_str, True, pygame.Color(0, 0, 0)),
            (SCREEN_WIDTH - 150, 0),
        )

        kills_str = f"Kills {score_tracker.scores[ScoreEventKind.EnemyKill]}"
        screen.blit(
            self.font.render(kills_str, True, pygame.Color(0, 0, 0)),
            (SCREEN_WIDTH - 150, 24),
        )

        if show_fps:
            fps_str = f"{clock.get_fps():.1f}"

            fps_overlay = self.font.render(fps_str, True, pygame.Color(0, 0, 0))

            screen.blit(fps_overlay, (0, 0))

        pygame.display.flip()


class BulletProcessor(esper.Processor):
    def process(self, *args, **kwargs):
        # TODO clean this up
        # could be more efficient than N^2

        for ent, (bullet, collidable, pos) in self.world.get_components(
            Bullet, Collidable, Position
        ):
            for other_ent, (
                enemy,
                other_collidable,
                other_pos,
            ) in self.world.get_components(Enemy, Collidable, Position):
                if check_collision(pos, collidable, other_pos, other_collidable):
                    logger.info("Destroying entity id=%d", other_ent)

                    track_score_event(self.world, ScoreEventKind.EnemyKill)

                    ## destroy enemy and self
                    self.world.delete_entity(other_ent)
                    self.world.delete_entity(ent)

                    break

            # cleanup: when bullet leaves world boundaries
            if (
                pos.x <= 0
                or pos.x >= SCREEN_WIDTH
                or pos.y <= 0
                or pos.y >= SCREEN_HEIGHT
            ):
                logger.info("Bullet out of bounds id=%d", ent)
                self.world.delete_entity(ent)


class PlayerInputProcessor(esper.Processor):
    def process(self, *args, **kwargs):
        # TODO consider sorting by keydown, then keyup,
        #   in case we receive a sequence "out of order" like
        #   [W key up, W key down]
        input_events = kwargs["player_input_events"]
        player_actions = []

        _, player_key_input = self.world.get_component(PlayerKeyInput)[0]

        for input_event in input_events:
            logger.debug(
                "Processing player input event kind=%d key=%d",
                input_event["kind"],
                input_event["key"],
            )

            match input_event:
                case {"kind": InputEventKind.KeyUp, "key": key}:
                    match key:
                        case pygame.constants.K_w:
                            player_actions.append(PlayerActionKind.StopAccelerating)
                        case pygame.constants.K_s:
                            player_actions.append(PlayerActionKind.StopDecelerating)
                case {"kind": InputEventKind.KeyDown, "key": key}:
                    match key:
                        case pygame.constants.K_w:
                            player_actions.append(PlayerActionKind.Accelerate)
                        case pygame.constants.K_s:
                            player_actions.append(PlayerActionKind.Decelerate)

        for action in player_actions:
            match action:
                case PlayerActionKind.Accelerate:
                    # could add/remove acceleration component instead of modifying
                    set_player_accelerating(self.world, True)
                case PlayerActionKind.StopAccelerating:
                    set_player_accelerating(self.world, False)
                case PlayerActionKind.Decelerate:
                    set_player_decelerating(self.world, True)
                case PlayerActionKind.StopDecelerating:
                    set_player_decelerating(self.world, False)


class ScoreTimeTrackerProcessor(esper.Processor):
    def process(self, *args, delta, **kwargs):
        for _, score_tracker in self.world.get_component(ScoreTracker):
            score_tracker.scores[ScoreEventKind.Time] += delta / 1_000.0
