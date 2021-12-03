import curses
from game import Game


def curses_main(screen):
    """Main function passed to wrapper"""
    tetris = Game(screen)
    tetris.run_game()


def main():
    """Runs the wrapper"""
    curses.wrapper(curses_main)


if __name__ == '__main__':
    main()
