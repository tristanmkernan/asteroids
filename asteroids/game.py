import pygame

from asteroids.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from asteroids.ecs.enums import InputEventKind
from asteroids.world import build_world


def play_game():
    #####
    # setup pygame
    #####

    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()

    #####
    # setup world
    #####

    world = build_world()

    #####
    # core game loop
    #####

    running = True

    while running:
        input_events = []

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    input_events.append(
                        {"kind": InputEventKind.KeyDown, "key": event.key}
                    )
                case pygame.KEYUP:
                    input_events.append(
                        {"kind": InputEventKind.KeyUp, "key": event.key}
                    )

        ms = clock.tick(30)

        world.process(
            delta=ms,
            clock=clock,
            screen=screen,
            show_fps=True,
            player_input_events=input_events,
        )

    pygame.quit()
