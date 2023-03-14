import logging
import sys

from asteroids.game import play_game


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


if __name__ == "__main__":
    play_game()
