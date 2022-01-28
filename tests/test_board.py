# region imports ----------------------------------------------------------------

import curses
import time
import pytest

from testing_tools import *

enable_import_from_game_dir()

from components import Board, Tile, Block
from game import GameEnded


# endregion


def test_board_init(game):
    b = Board(game)


def test_board_clear(board, game):
    for i in range(10):
        board._grid[i][2 * i] = Tile(game, (i, 2 * i), curses.color_pair(1))
    board._block = Block(game, 3)

    board.clear()

    assert not any([item for column in board._grid for item in column])
    assert not board._block


def test_board_get_tile(board, game):
    for i in range(10):
        board._grid[i][2 * i] = Tile(game, (i, 2 * i), curses.color_pair(1))

    assert board.get_tile(3, 6).position == (3, 6)
    assert not board.get_tile(3, 7)


def test_board_tiles(board, game, tile_eq):
    for i in range(10):
        board._grid[i][2 * i] = Tile(game, (i, 2 * i), curses.color_pair(1))

    loose_tiles = [Tile(game, (i, 2 * i), curses.color_pair(1)) for i in range(10)]
    assert len(loose_tiles) == len(board.tiles)
    assert all([tile in loose_tiles for tile in set(board.tiles)])


def test_board_tile_positions(board, game, tile_eq):
    for i in reversed(range(10)):
        board._grid[i][2 * i] = Tile(game, (i, 2 * i), curses.color_pair(1))

    for x in range(len(board._grid)):
        for y in range(len(board._grid[0])):
            if board._grid[x][y] and board._grid[x][y].position != (x, y):
                assert False


def test_board_add_to_grid(board, game):
    my_tiles = [Tile(game, (i, 3 * i), curses.color_pair(1)) for i in range(7)]

    board._add_to_grid(my_tiles)

    assert all([board._grid[i][3 * i].position == (i, 3 * i) for i in range(7)])


def test_board_get_full_row_idx(board, game):
    my_tiles = [Tile(game, (i, 7), curses.color_pair(1)) for i in range(10)]
    my_tiles.extend([Tile(game, (3, 5), curses.color_pair(1)), Tile(game, (4, 5), curses.color_pair(1))])

    board._add_to_grid(my_tiles)

    assert board._get_full_rows_idx({5, 6, 7, 8, 9}) == [7]
    assert board._get_full_rows_idx({1, 2}) == []


def test_board_remove_full_rows(board, game):
    my_tiles = [Tile(game, (i, 7), curses.color_pair(1)) for i in range(10)]
    my_tiles.extend([Tile(game, (3, 5), curses.color_pair(1)), Tile(game, (4, 5), curses.color_pair(1))])
    board._add_to_grid(my_tiles)

    board._remove_full_rows([])
    assert all(tile in board.tiles for tile in my_tiles)

    board._remove_full_rows([6, 7, 8])
    assert len(board.tiles) == 2


def test_board_spawn_block(board, game, monkeypatch):
    monkeypatch.setattr('components.randint', mock_factory(3))
    block = Block(game, 3)
    board._spawn_block(block)

    assert board._block == block
    assert set(board._block.tile_positions) == {(3, 0), (4, 0), (3, 1), (4, 1)}

    monkeypatch.setattr('components.Block.validate_position', mock_factory(False))
    with pytest.raises(GameEnded):
        board._spawn_block(block)


def test_board_handle_bottom_collisions(board, game, monkeypatch):
    block = Block(game, 3)
    board._block = block
    board._block._points = 999
    board._block.set_position(0, 5)
    board._add_to_grid([Tile(game, (i, 5), curses.color_pair(1)) for i in range(2, 10)])
    board.state = board.soft_drop

    board.handle_bottom_collision()

    assert game._points == 1099
    assert game._cleared_lines == 1
    assert board.block is not block
    assert board.state == board.falling
    assert len(board.tiles) == 2


def test_board_update(board, game, monkeypatch, silence_keyboard):
    monkeypatch.setattr('time.time', time.time_ns)
    monkeypatch.setattr('components.randint', mock_factory(3))

    board = game._board

    block = Block(game, 3)

    board._spawn_block(block)
    board._block.set_position(4, 3)
    game.board._add_to_grid([Tile(game, (4, 5), curses.color_pair(1))])
    board.update()

    assert len(board.tiles) == 5
