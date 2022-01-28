# region imports ----------------------------------------------------------------

import curses
import pytest

from testing_tools import *

enable_import_from_game_dir()

from components import Board, Tile, Block


# endregion


def test_block_init(game):
    b = Block(game, 3)


def test_block_set_position(game):
    block = Block(game, 4)
    block.set_position(6, 12)

    assert set(block.tile_positions) == {(6, 13), (7, 13), (7, 12), (8, 12)}


def test_block_update(game):
    block = Block(game, 1)
    block.set_position(3, 4)
    block.update(-1, 2)

    assert set(block.tile_positions) == {(2, 6), (2, 7), (3, 7), (4, 7)}


def test_block_get_rotated_positions(game):
    block = Block(game, 6)
    block.set_position(2, 2)
    positions = block._get_rotated_positions(1)
    assert set(positions) == {(3, 1), (3, 2), (2, 3), (2, 2)}

    block = Block(game, 0)
    block.set_position(2, 2)

    positions = block._get_rotated_positions(1)
    assert set(positions) == {(4, 4), (4, 1), (4, 2), (4, 3)}


def test_block_rotate(game):
    block = Block(game, 2)
    block.set_position(2, 2)
    block.rotate(1)
    assert set(block.tile_positions) == {(2, 1), (2, 2), (2, 3), (3, 3)}

    block = Block(game, 0)
    block.set_position(2, 2)
    block.rotate(1)
    assert set(block.tile_positions) == {(4, 4), (4, 1), (4, 2), (4, 3)}


def test_block_validate_position(game):
    board = game._board
    block = Block(game, 5)
    assert block.validate_position(block.tile_positions)
    block.set_position(9, 5)
    assert not block.validate_position(block.tile_positions)
    block.set_position(0, 11)
    assert block.validate_position(block.tile_positions)
    block.set_position(-1, 15)
    assert not block.validate_position(block.tile_positions)
    block.set_position(4, 19)
    assert not block.validate_position(block.tile_positions)

    board._add_to_grid([Tile(game, (5, 5), curses.color_pair(1))])
    block.set_position(4, 3)
    assert block.validate_position(block.tile_positions)


def test_board_check_side_collisions(game):
    board = game._board
    block = Block(game, 1)
    block.set_position(0, 3)
    assert block.check_side_collisions(-1)
    block.set_position(7, 15)
    assert block.check_side_collisions(1)
    board._add_to_grid([Tile(game, (5, 5), curses.color_pair(1))])
    block.set_position(2, 4)
    assert block.check_side_collisions(1)
    block.set_position(6, 4)
    assert block.check_side_collisions(-1)
    block.set_position(1, 1)
    assert not block.check_side_collisions(1)
    assert not block.check_side_collisions(-1)


def test_block_check_bottom_collisions(game):
    board = game._board
    block = Block(game, 0)
    assert not block.check_bottom_collisions()
    block.set_position(3, 19)
    assert block.check_bottom_collisions()
    board._add_to_grid([Tile(game, (4, 7), curses.color_pair(1))])
    block.set_position(3, 6)
    assert block.check_bottom_collisions()
