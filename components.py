from __future__ import annotations
import curses
import random
import time
from abc import ABC, abstractmethod
# from game import Game  # cannot be used - circular import
from random import randint
from typing import Tuple, List
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

    def draw(self, *args, **kwargs):
        """
        Draws the tile onto the screen
        :return:
        """
        try:
            self.screen.addch(self.y, self.x, self._char, self._typeface)
        except curses.error:
            pass  # uhhhhhhh

    def update(self, x: int, y: int):
        """
        Updates tile's position by a given offset
        :param x: X offset
        :param y: Y offset
        """
        self.x += x
        self.y += y


class BlockPreset(Component):  # NOT the best way to keep presets
    def __init__(self, game):
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

    def update(self, *args, **kwargs):
        super().update()

    def draw(self):
        super().draw()


class Block(BlockPreset):
    def __init__(self, game, block_id: int, x):
        super(Block, self).__init__(game)
        self.tiles = [Tile(self.game, (position[0] + x, position[1]), self.color_presets[block_id])
                      for position in self.block_presets[block_id]]
        self.tile_positions = self.update_tile_positions()

    def update(self, x: int, y: int):
        for tile in self.tiles:
            tile.update(x, y)

        self.tile_positions = self.update_tile_positions()

    def update_tile_positions(self) -> List[Tuple[int, int]]:
        return [(tile.x, tile.y) for tile in self.tiles]

    def draw(self, *args, **kwargs):
        for tile in self.tiles:
            tile.draw()

    def check_collisions(self, x, y):
        fields_to_check = [(tile.x + x, tile.y + y)
                           for tile in self.tiles
                           if (tile.x + x, tile.y + y) not in self.tile_positions]
        return self.check_block_collisions(fields_to_check) \
               or self.check_bottom_edge(fields_to_check, y) \
               or self.check_sides(fields_to_check, x)

    def check_block_collisions(self, fields_to_check):

        return any(field in self.game.board.tile_positions for field in
                   fields_to_check)

    def check_bottom_edge(self, fields_to_check, y):
        if y:
            # sys.exit()
            return any(field[1] == self.game.board.size_y for field in fields_to_check)
        return False

    def check_sides(self, fields_to_check, x):
        if x:
            return any(field[0] < 0 or field[0] == self.game.board.size_x for field in fields_to_check)
        return False


class BoardState(ABC):
    @staticmethod
    @abstractmethod
    def update(board, key):
        pass


class SoftDrop(BoardState):
    @staticmethod  # could not reference self.board, as class instances were initialized during
    # Board class initialization
    def update(board, key=None):
        key_mapping = {260: (-1, 0),
                       261: (1, 0)}
        direction = key_mapping.get(key, None)
        if direction:
            if not board.block.check_collisions(*direction):  # checks only L/R collisions
                board.block.update(*direction)

        if (time.time() - board.last_block_move) > board.period:  # move down
            board.block.update(0, 1)
            board.last_block_move = time.time()


class HardDrop(BoardState):
    @staticmethod
    def update(board, key=None):  # just move down lol
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
        self.tile_positions = []  # FIXME sub-optimal
        self.rows = [[] for _ in range(self.size_y)]

        # timing
        self.period = game.settings.BLOCK_MOVEMENT_PERIOD
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
            if self.block.check_collisions(0, 1):
                self.tiles.extend(self.block.tiles)
                self.tile_positions.extend(self.block.tile_positions)

                for tile in self.block.tiles:
                    self.rows[tile.y].append(tile)

                # self.delete_full_rows()

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

            self.block = Block(self.game, randint(0, 6), randint(0, 6))

    # def delete_full_rows(self):  # TODO Does not work # check if rows are full
    # TODO rework tile storing
    #  mechanism, rows and positions cannot be stored separetely from tiles, as it leads to unresolvable errors


    #  rows_to_check = {tile.y-1 for tile in self.block.tiles}
    #
    #     rows_to_add = 0
    #     for row_idx in rows_to_check:
    #         if len(self.rows[row_idx]) == 0:
    #             # remove from self.rows
    #             for popped_tile in self.rows.pop(row_idx):
    #                 # remove tiles from self.tiles
    #                 print((popped_tile.x, popped_tile.y))
    #                 self.tile_positions.remove((popped_tile.x, popped_tile.y))
    #
    #                 self.tiles.remove(popped_tile)
    #
    #             for tile in self.tiles:
    #                 tile.y += 1
    #             for pos in self.tile_positions:
    #                 self.tile_positions.remove(pos)
    #                 self.tile_positions.append((pos[0], pos[1]+ 1))
    #
    #
    #                 # del popped_tile  # does not do anything (?)
    #
    #             # insert a new row on top to compensate for the popped one
    #             rows_to_add += 1
    #     self.rows.insert(rows_to_add, [])

# TODO docstrings
