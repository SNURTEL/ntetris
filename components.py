from __future__ import annotations
import curses
import time
from abc import ABC, abstractmethod
# from game import Game  # cannot be used - circular import
from random import randint
from typing import Tuple, List, Set
import sys


# TODO USE PRIVATE ATTRIBUTES!!!1!!111!1!1ONEONE

class Component(ABC):
    """
    Composite abstract class used to build other classes
    """

    def __init__(self, game):
        """
        Inits class Component
        :param game: Game instance passed by the game itself
        """
        self.game = game
        self.screen = game.screen
        self.settings = game.settings

    @abstractmethod
    def draw(self, *args, **kwargs):
        """
        Draws the component onto the screen
        :param args: Ignored
        :param kwargs: Ignored
        """
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        """
        Updates the component's state
        :param args: Ignored
        :param kwargs: Ignored
        """
        pass


class Tile(Component):
    """
    Class representing a tile on a Tetris board
    """

    def __init__(self, game, position: Tuple[int, int], color):
        """
        Inits class Tile
        :param game: Game instance passed by the game itself
        :param position: Initial tile position (x, y)
        :param color: A curses.colorpair-like object indicating tile's appearance
        """
        super(Tile, self).__init__(game)
        self._char = '#'
        self._typeface = color
        self.x, self.y = position

    @property
    def position(self):
        return self.x, self.y

    def draw(self, *args, **kwargs):
        """
        Draws the tile onto the screen
        :return:
        """
        try:
            self.screen.addch(self.y, self.x, self._char, self._typeface)
        except curses.error:
            pass  # uhhhhhhh this WILL cause errors

    def update(self, x: int, y: int):
        """
        Updates tile's position by a given offset
        :param x: X offset
        :param y: Y offset
        """
        self.x += x
        self.y += y


class BlockPreset(Component):  # NOT the best way to keep presets
    """
    Keeps all the information necessary for creating new blocks
    """

    def __init__(self, game):
        """
        Inits class BlockPreset
        :param game: Game instance passed by the game itself
        """
        super(BlockPreset, self).__init__(game)
        # ugly; block presets
        self.block_presets = (
            #       ####  0 cyan
            [(pos, 0) for pos in range(4)],
            #       #
            #       ####  1 blue
            [(pos, 1) for pos in range(4)] + [(0, 0)],
            #          #
            #       ####  2 orange
            [(pos, 1) for pos in range(4)] + [(3, 0)],
            #       ##
            #       ##  3 yellow
            [(0, 0), (0, 1), (1, 0), (1, 1)],
            #        ##
            #       ##   4 green
            [(1, 0), (2, 0), (0, 1), (1, 1)],
            #        #
            #       ###  5 magenta
            [(pos, 1) for pos in range(4)] + [(1, 0)],
            #        ##
            #       ##   6 red
            [(0, 0), (1, 0), (1, 1), (2, 1)]
        )
        self.color_presets = (curses.color_pair(11), curses.color_pair(12), curses.color_pair(13), curses.color_pair(
            14), curses.color_pair(15), curses.color_pair(16), curses.color_pair(17))

    def update(self, *args, **kwargs) -> None:
        """
        Updates the block's position
        :param args: Ignored
        :param kwargs: Ignored
        """
        super().update()

    def draw(self) -> None:
        """
        Draws the block onto the screen
        """
        super().draw()


class Block(BlockPreset):
    """
    Class representing a block of tiles. When the block is placed, tiles are moved to board.tiles and
    the class instance is deleted
    """

    def __init__(self, game, block_id: int, x: int):
        """
        Inits class Block
        :param game: Game instance passed by the game itself
        :param block_id: Indicates which block to spawn, block presets are stored in the superclass
        :param x: Indicates where to spawn the block, corresponds to block's upper left corner
        """
        super(Block, self).__init__(game)
        self.tiles = [Tile(self.game, (position[0] + x, position[1]), self.color_presets[block_id])
                      for position in self.block_presets[block_id]]

    def update(self, x: int, y: int):
        """
        Updated the block's position by a given offset
        :param x: X offset
        :param y: Y offset
        """
        for tile in self.tiles:
            tile.update(x, y)

    def draw(self, *args, **kwargs):
        """
        Draws the block onto the screen
        :param args: Ignored
        :param kwargs: Ignored
        """
        for tile in self.tiles:
            tile.draw()

    def check_side_collisions(self, x: int) -> bool:
        """
        Checks if the block is located next to a tile or at the board's edge
        :param x: Indicates the direction in which the check should be performed
        :return: True if the block is located next to a tile or at the board's edge, False if it's not
        """
        fields_to_check = self._get_fields_to_check(x, 0)
        return self._check_block_collisions(fields_to_check) or self._check_sides(fields_to_check)

    def check_bottom_collisions(self):
        """
        Checks if the block is located on top of a tile or at the board's bottom edge
        :return: True if the block is located on top of a tile or at the board's bottom edge, False if it's not
        """
        fields_to_check = self._get_fields_to_check(0, 1)
        return self._check_block_collisions(fields_to_check) or self._check_bottom_edge(fields_to_check)

    def _get_fields_to_check(self, x: int, y: int) -> Set[Tuple[int, int]]:
        """
        Generates (self.x + x,self.y + y) pairs which will later be checked if they contain any obstacles
        :param x: X offset
        :param y: Y offset
        :return: A set of (x, y) pairs
        """
        return {(tile.x + x, tile.y + y) for tile in self.tiles}

    def _check_block_collisions(self, fields_to_check: Set[Tuple[int, int]]) -> bool:
        """
        Checks for potential collision with other tiles
        :param fields_to_check: (x, y) pairs to be checked if they contain a tile
        :return: True if at least one of fields_to_check contains a tile, False if it does not
        """
        board_tile_positions = {tile.position for tile in self.game.board.tiles}
        return bool(board_tile_positions.intersection(fields_to_check))

    def _check_bottom_edge(self, fields_to_check: Set[Tuple[int, int]]) -> bool:
        """
        Checks if the block sits at the board's bottom edge
        :param fields_to_check: (x, y) pairs to be checked if they are located below board's bottom edge
        :return: True if the block sits at the board's bottom edge, false if it does not
        """
        return any(field[1] == self.game.board.size_y for field in fields_to_check)

    def _check_sides(self, fields_to_check: Set[Tuple[int, int]]) -> bool:
        """
        Checks if the block is located next to the board's edge
        :param fields_to_check: (x, y) pairs to be checked if any of them is not located on the board
        :return: True if the block is located next to the board's edge, False if it's not
        """
        return any(field[0] < 0 or field[0] == self.game.board.size_x for field in fields_to_check)


class BoardState(ABC):
    """
    Base class for classes indicating the ways in which the board should be updated
    """
    @staticmethod  # could not reference self.board, as class instances were initialized during
    # Board class initialization
    @abstractmethod
    def update(board: Board, key: int):
        """
        Moves the tiles and / or the current block and handles user input
        :param board: Board class instance passed by the board itself
        :param key: Keyboard key id extracted by curses.getch
        """
        pass


class SoftDrop(BoardState):
    """
    Game state handling events if the down arrow key was not yet pressed
    """
    @staticmethod
    def update(board: Board, key: int):
        """
        Handles horizontal movement on key press and moves the tile down if board.block_move_period passed
        :param board: Board class instance passed by the board itself
        :param key: Keyboard key id extracted by curses.getch
        """
        # handle horizontal movement
        key_mapping = {260: -1,
                       261: 1}
        x_direction = key_mapping.get(key, None)
        if x_direction:
            if not board.block.check_side_collisions(x_direction):
                board.block.update(x_direction, 0)

        # handle vertical movement
        if (time.time() - board.last_block_move) > board.block_move_period:
            board.block.update(0, 1)
            board.last_block_move = time.time()


class HardDrop(BoardState):
    """
    Game state handling events if arrow down key was pressed
    """
    @staticmethod
    def update(board: Board, key=None):
        """
        Moves the tiles down by 1 field
        :param board: Board class instance passed by the board itself
        :param key: Ignored
        """
        board.block.update(0, 1)


class Board(Component):
    """
    Class representing a Tetris board
    """

    def __init__(self, game):
        """
        Inits class Board
        Board dimensions are extracted from game's settings
        :param game: Game instance passed by the game itself
        """
        super(Board, self).__init__(game)

        # board size
        self.size_x = self.settings.BOARD_SIZE[0]
        self.size_y = self.settings.BOARD_SIZE[1]

        # tiles
        self.tiles = []
        self.block = None

        # timing
        self.block_move_period = game.settings.BLOCK_MOVEMENT_PERIOD
        self.last_block_move = time.time()

        # event handling
        self.soft_drop = SoftDrop()
        self.hard_drop = HardDrop()
        self.state = SoftDrop

    def draw(self) -> None:
        """
        Draws the board
        """
        for tile in self.tiles:
            tile.draw()
        try:
            self.block.draw()
        except AttributeError:
            pass

    def update(self, key: int) -> None:
        """
        Moves the tiles if necessary / removes tiles / spawns new tiles
        :param key: Key code passed by curses.getch
        """

        try:  # or if self.block
            # if block lies on top of another block / on the bottom edge
            if self.block.check_bottom_collisions():

                # move tiles from block.tiles to self.tiles and delete the block object
                self.tiles.extend(self.block.tiles)

                # check if any rows are full
                rows_to_delete = self.get_full_rows_idx({tile.y for tile in self.block.tiles})

                if rows_to_delete:
                    # remove full rows
                    self.tiles = [tile for tile in self.tiles if tile.y not in rows_to_delete]

                    # move tiles down
                for tile in self.tiles:
                    tile.update(0, sum(tile.y < row_idx for row_idx in rows_to_delete))

                del self.block
                return

            if key == 258:  # down arrow
                self.state = self.hard_drop

            # update block position, either move down (HardDrop) or
            # handle keypresses and move down if enough time passed (SoftDrop)
            self.state.update(self, key)

        except AttributeError:  # or else
            # spawn a new block
            self.state = self.soft_drop

            self.block = Block(self.game, randint(0, 6), randint(0, self.size_x - 4))

    def get_full_rows_idx(self, to_check: Set[int]) -> List[int]:
        tile_y = [tile.y for tile in self.tiles]
        return [idx for idx in to_check if tile_y.count(idx) == self.size_x]
