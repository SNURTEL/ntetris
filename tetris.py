import curses
import os
import sys

from src.game import run_game


def main(args):
    os.environ.setdefault('ESCDELAY', '25')

    curses.wrapper(run_game)
    curses.endwin()


if __name__ == '__main__':
    main(sys.argv)
