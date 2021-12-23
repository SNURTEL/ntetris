from __future__ import annotations
import curses
import time
from abc import ABC, abstractmethod
# from game import Game  # cannot be used - circular import
from random import randint
from typing import Tuple, List


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
        self.current_block = []

        # timing
        self.period = game.settings.BLOCK_MOVEMENT_PERIOD
        self.last_block_move = time.time()
        self.nowait = False
        self.new_block = True

        # ugly; block presets
        self.blocks = (
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
        self.block_colors = (curses.color_pair(11), curses.color_pair(12), curses.color_pair(13), curses.color_pair(
            14), curses.color_pair(15), curses.color_pair(16), curses.color_pair(17))

    def draw(self) -> None:
        """
        Draws the board
        """
        for tile in self.tiles:
            tile.draw()

    def update(self, key: int) -> None:  # FIXME not the most elegant
        """
        Moves the tiles if necessary / removes tiles / spawns new tiles
        :param key: Key code passed by curses.getch
        """
        tiles_to_move = self.current_block

        if tiles_to_move:

            # move tiles
            if not self.nowait:
                # handle horizontal movement
                if key == 260:  # move left
                    self.move_tiles(tiles_to_move, -1, 0)
                    self.new_block = False
                elif key == 261:  # move right
                    self.move_tiles(tiles_to_move, 1, 0)
                    self.new_block = False

                # handle vertical movement
                elif key == 258 and not self.new_block:
                    self.nowait = True
                else:
                    self.new_block = False

            # move down
            if (time.time() - self.last_block_move) > self.period or self.nowait:
                self.move_tiles(tiles_to_move, 0, 1)
                self.last_block_move = time.time()

            # self.current_block is cleared on collision in

        else:
            # spawn a new block
            self.add_block(randint(0, 6), randint(0, 6))
            self.nowait = False
            self.new_block = True

    def delete_row(self, row: int):
        """
        Deletes all tiles in a row
        :param row: Row index
        """
        tiles_to_delete = [self.tiles.index(tile) for tile in self.tiles if tile.y == row]
        for idx in reversed(tiles_to_delete):
            del self.tiles[idx]

    def move_tiles(self, tiles_to_move: List[Tile], x: int, y: int):
        """
        Moves the tiles by a given offset (if possible)
        :param tiles_to_move: A list of tiles to be moved, should correspond to a block
        :param x: X offset
        :param y: Y offset
        """
        tiles_to_move = tiles_to_move.copy()  # TODO maybe rework this

        if not any(tile.y == self.size_y-1 for tile in self.current_block):
            if x and not all(0 <= tile.x + x <= self.size_x - 1 for tile in tiles_to_move):
                x = 0
            for _ in range(len(tiles_to_move)):
                tile = tiles_to_move.pop(0)
                tile.update(x, y)
        else:
            # clear current block
            self.current_block.clear()

        # tile_positions = {tile.x for tile in self.tiles}  # FIXME the dumb way, does not work
        # block_positions = {tile.x + x for tile in self.current_block}
        #
        # if not tile_positions.intersection(block_positions):
        #     # move block if no collisions
        #     if x and not all(0 <= tile.x + x <= self.size_x - 1 for tile in tiles_to_move):
        #         x = 0
        #     for _ in range(len(tiles_to_move)):
        #         tile = tiles_to_move.pop(0)
        #         tile.update(x, y)
        # else:
        #     # clear current block
        #     self.current_block.clear()

    def add_block(self, block_id: int, x: int):
        """
        Adds a block of tiles to the board at a given x position
        :param block_id: Id used to access self.blocks and self.block_colors, containing, respectively, positions of
        tiles within a block and block colors (both matching original Tetris tetrominoes)
        :param x: Indicates where to spawn the block
        """

        new_block = [Tile(self.game, (position[0] + x, position[1]), self.block_colors[block_id])
                     for position in self.blocks[block_id]]

        self.tiles.extend(new_block)
        self.current_block.extend(new_block)
        #
        # for position in self.blocks[block_id]:
        #     self.tiles.append(Tile(self.game, (position[0] + x, position[1]), self.block_colors[block_id]))
