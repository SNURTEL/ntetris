import curses
import os

from game import Game


def curses_main(screen):
    """Main function passed to wrapper"""
    tetris = Game(screen)
    tetris.run_game()


def main():
    """Runs the wrapper"""
    # remove the 1s delay on esc key press
    os.environ.setdefault('ESCDELAY', '25')

    curses.wrapper(curses_main)


if __name__ == '__main__':
    main()
