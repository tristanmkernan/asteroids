import logging

import esper
import pygame
import pygame.constants

from asteroids.constants import SCREEN_HEIGHT, SCREEN_WIDTH


from .components import (
    Acceleration,
    Asteroid,
    Bullet,
    BulletAmmo,
    Collidable,
    Lifetime,
    PlayerKeyInput,
    PlayerShip,
    Position,
    RenderableCollection,
    Rotation,
    Velocity,
    Spawning,
    Renderable,
    ScoreTracker,
)
from .entities import (
    create_bullet,
    set_player_acceleration,
    set_player_rotating_left,
    set_player_rotating_right,
    spawn_asteroid,
    track_score_event,
)
from .enums import RenderableKind, ScoreEventKind, InputEventKind, PlayerActionKind
from .ui import render
from .utils import check_collision


logger = logging.getLogger(__name__)


def add_systems(world: esper.World):
    world.add_processor(MovementProcessor())
    world.add_processor(RenderingProcessor())
    world.add_processor(SpawningProcessor())
    world.add_processor(BulletProcessor())
    world.add_processor(PlayerInputProcessor())
    world.add_processor(ScoreTimeTrackerProcessor())
    world.add_processor(BulletAmmoProcessor())
    world.add_processor(PlayerMovementVisualEffectProcessor())
    world.add_processor(LifetimeProcessor())


class MovementProcessor(esper.Processor):
    def process(self, *args, delta, **kwargs):
        # update rotation
        for _, (rot, pos) in self.world.get_components(Rotation, Position):
            pos.rotation += rot.speed * delta
            pos.normalize_rotation()

        # update velocity
        for ent, (vel, acc) in self.world.get_components(Velocity, Acceleration):
            vel.x += acc.x * delta
            vel.y += acc.y * delta

            vel.clamp()

        # update position
        for ent, (vel, pos) in self.world.get_components(Velocity, Position):
            pos.x += vel.x * delta
            pos.y += vel.y * delta

            # TODO this might need to be a separate processor
            # handle screen crossings
            if pos.x > SCREEN_WIDTH:
                pos.x = 0.0
            elif pos.x < 0.0:
                pos.x = SCREEN_WIDTH

            if pos.y > SCREEN_HEIGHT:
                pos.y = 0.0
            elif pos.y < 0.0:
                pos.y = SCREEN_WIDTH


class SpawningProcessor(esper.Processor):
    def process(self, *args, delta, **kwargs):
        for ent, spawning in self.world.get_component(Spawning):
            spawning.elapsed += delta

            if spawning.elapsed > spawning.every:
                asteroid = spawn_asteroid(self.world)

                logger.info("Spawned new asteroid id=%d", asteroid)

                spawning.elapsed = 0.0


class RenderingProcessor(esper.Processor):
    def __init__(self) -> None:
        super().__init__()

        self.font = pygame.font.SysFont("Comic", 40)

    def process(self, *args, **kwargs):
        show_fps = kwargs["show_fps"]
        screen = kwargs["screen"]
        clock = kwargs["clock"]

        screen.fill((255, 255, 255))

        # simple renderables
        for ent, (renderable, pos) in self.world.get_components(Renderable, Position):
            render(screen, renderable, pos)

        # grouped renderables
        for _, (renderables, pos) in self.world.get_components(
            RenderableCollection, Position
        ):
            for renderable in renderables.items:
                render(screen, renderable, pos)

        _, score_tracker = self.world.get_component(ScoreTracker)[0]
        _, (_, bullet_ammo) = self.world.get_components(PlayerShip, BulletAmmo)[0]

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

        ammo_str = f"Ammo {bullet_ammo.count}"
        screen.blit(
            self.font.render(ammo_str, True, pygame.Color(0, 0, 0)),
            (SCREEN_WIDTH - 150, 48),
        )

        if show_fps:
            fps_str = f"{clock.get_fps():.1f}"

            fps_overlay = self.font.render(fps_str, True, pygame.Color(0, 0, 0))

            screen.blit(fps_overlay, (0, 0))

        pygame.display.flip()


class BulletAmmoProcessor(esper.Processor):
    def process(self, *args, delta, **kwargs):
        for ent, (player_ship, bullet_ammo) in self.world.get_components(
            PlayerShip, BulletAmmo
        ):
            bullet_ammo.elapsed = min(
                bullet_ammo.elapsed + delta, bullet_ammo.every + delta
            )

            if not bullet_ammo.full and bullet_ammo.elapsed > bullet_ammo.every:
                bullet_ammo.count = min(bullet_ammo.count + 1, bullet_ammo.max)

                bullet_ammo.elapsed = 0.0


class BulletProcessor(esper.Processor):
    def process(self, *args, **kwargs):
        # TODO clean this up
        # could be more efficient than N^2

        for ent, (bullet, collidable, pos) in self.world.get_components(
            Bullet, Collidable, Position
        ):
            for other_ent, (
                asteroid,
                other_collidable,
                other_pos,
            ) in self.world.get_components(Asteroid, Collidable, Position):
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
                    player_key_input.keydowns.discard(key)

                    match key:
                        case pygame.constants.K_w:
                            player_actions.append(PlayerActionKind.StopAccelerating)
                        case pygame.constants.K_s:
                            player_actions.append(PlayerActionKind.StopDecelerating)
                        case pygame.constants.K_a:
                            player_actions.append(PlayerActionKind.StopRotateLeft)
                        case pygame.constants.K_d:
                            player_actions.append(PlayerActionKind.StopRotateRight)
                        case pygame.constants.K_SPACE:
                            player_actions.append(PlayerActionKind.Fire)
                case {"kind": InputEventKind.KeyDown, "key": key}:
                    player_key_input.keydowns.add(key)

        # keydowns are updated every frame
        # e.g. to accelerate in rotated direction
        for key in player_key_input.keydowns:
            match key:
                case pygame.constants.K_w:
                    player_actions.append(PlayerActionKind.Accelerate)
                case pygame.constants.K_s:
                    player_actions.append(PlayerActionKind.Decelerate)
                case pygame.constants.K_a:
                    player_actions.append(PlayerActionKind.RotateLeft)
                case pygame.constants.K_d:
                    player_actions.append(PlayerActionKind.RotateRight)

        for action in player_actions:
            match action:
                case PlayerActionKind.Accelerate:
                    # could add/remove acceleration component instead of modifying
                    set_player_acceleration(self.world, forward=True)
                case PlayerActionKind.StopAccelerating:
                    set_player_acceleration(self.world, unset=True)
                case PlayerActionKind.Decelerate:
                    set_player_acceleration(self.world, forward=False)
                case PlayerActionKind.StopDecelerating:
                    set_player_acceleration(self.world, unset=True)
                case PlayerActionKind.Fire:
                    create_bullet(self.world)
                case PlayerActionKind.RotateLeft:
                    set_player_rotating_left(self.world, True)
                case PlayerActionKind.StopRotateLeft:
                    set_player_rotating_left(self.world, False)
                case PlayerActionKind.RotateRight:
                    set_player_rotating_right(self.world, True)
                case PlayerActionKind.StopRotateRight:
                    set_player_rotating_right(self.world, False)


class ScoreTimeTrackerProcessor(esper.Processor):
    def process(self, *args, delta, **kwargs):
        for _, score_tracker in self.world.get_component(ScoreTracker):
            score_tracker.scores[ScoreEventKind.Time] += delta / 1_000.0


class PlayerMovementVisualEffectProcessor(esper.Processor):
    elapsed = 0.0

    def process(self, *args, delta, **kwargs):
        self.elapsed += delta

        _, (_, pos, vel) = self.world.get_components(PlayerShip, Position, Velocity)[0]

        # spawn new visual effect
        if self.elapsed > 250.0 and vel.magnitude > 0.20:
            logger.debug("Spawning movement visual effect")

            self.world.create_entity(
                Position(x=pos.x, y=pos.y),
                Lifetime(remaining=2.0 * 1_000.0),
                Renderable(kind=RenderableKind.Circle, color=(125, 125, 125), radius=3),
            )

            self.elapsed = 0.0


class LifetimeProcessor(esper.Processor):
    def process(self, *args, delta, **kwargs):
        for ent, lifetime in self.world.get_component(Lifetime):
            lifetime.remaining -= delta

            if lifetime.remaining < 0.0:
                self.world.delete_entity(ent)
