import curses
import os
import sys

from src.game import run_game


def main(args):
    """Runs the wrapper"""
    # remove the 1s delay on esc key press
    os.environ.setdefault('ESCDELAY', '25')

    curses.wrapper(run_game)


if __name__ == '__main__':
    main(sys.argv)
