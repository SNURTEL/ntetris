# region imports ----------------------------------------------------------------

import pytest
import json
from io import StringIO
import os
import sys


def enable_import_from_game_dir():
    cwd = os.path.realpath(__file__)
    pd = os.path.sep.join(cwd.split(os.path.sep)[:-2]) + f'{os.path.sep}not_tetris'

    sys.path.append(pd)


enable_import_from_game_dir()

from game import Game
from components import Board, Tile


# endregion


# region mocks ----------------------------------------------------------------

def mock_factory(return_value):
    def mock_fun(*args, **kwargs):
        return return_value

    return mock_fun


def exception_raiser_factory(e):
    def mock_fun(*args, **kwargs):
        raise e

    return mock_fun


def empty_function(*args, **kwargs):
    return 0


# endregion
# region fixtures ----------------------------------------------------------------

@pytest.fixture(autouse=True)
def silence_curses(monkeypatch):
    # monkeypatch functions
    funs = ['cbreak', 'color_pair', 'curs_set', 'use_default_colors', 'init_color', 'init_pair', 'is_term_resized',
            'endwin']
    for fun in funs:
        monkeypatch.setattr(f'curses.{fun}', empty_function)

    # monkeypatch constants
    consts = ['A_BOLD', 'A_BLINK']
    for const in consts:
        monkeypatch.setattr(f'curses.{const}', 0)


@pytest.fixture(autouse=True)
def silent_screen():
    class Screen:
        def empty(self, *args, **kwargs):
            pass

        def __getattr__(self, item):
            return self.empty

        def subwin(self, *args, **kwargs):
            return Screen()

    return Screen()


@pytest.fixture
def game(silent_screen, mock_json_operations, monkeypatch):
    monkeypatch.setattr('sys.argv', [''])
    return Game(silent_screen)


@pytest.fixture
def board(game, mock_json_operations):
    return Board(game)


@pytest.fixture
def scoreboard_io():
    return StringIO('{"scoreboard": [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]}')


@pytest.fixture
def mock_json_operations(monkeypatch, scoreboard_io):
    def write_scoreboard(fp, scoreboard, *args, **kwargs):
        json.dump({'scoreboard': scoreboard}, scoreboard_io)

    def read_scoreboard(fp, *args, **kwargs):
        scoreboard_io.seek(0)
        return json.load(scoreboard_io)['scoreboard']

    def save_scoreboard(self, scoreboard: list, *args, **kwargs):
        scoreboard_io.seek(0)
        write_scoreboard(scoreboard_io, scoreboard)
        scoreboard_io.truncate()

    def load_scoreboard(self, *args, **kwargs):
        scoreboard_io.seek(0)
        return read_scoreboard(scoreboard_io)

    monkeypatch.setattr('game.Game._save_scoreboard', save_scoreboard)
    monkeypatch.setattr('game.Game._load_scoreboard', load_scoreboard)
    monkeypatch.setattr('game.Game._read_scoreboard', read_scoreboard)
    monkeypatch.setattr('game.Game._write_scoreboard', write_scoreboard)

    return scoreboard_io


@pytest.fixture
def silence_keyboard(monkeypatch):
    monkeypatch.setattr('keyboard.is_pressed', mock_factory(False))


@pytest.fixture
def tile_eq(monkeypatch):
    def eq(self, tile):
        return self.position == tile.position and self._typeface == tile._typeface and self._chars == tile._chars

    monkeypatch.setattr('components.Tile.__eq__', eq)

# endregion
# ----------------------------------------------------------------
