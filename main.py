import pygame
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
