from pathlib import Path
import sys

import pygame


SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from game import Game


def main() -> None:
    pygame.mixer.pre_init(44100, -16, 2, 256)
    pygame.init()
    game = Game()
    game.run()
    game.shutdown()
    pygame.quit()


if __name__ == "__main__":
    main()
