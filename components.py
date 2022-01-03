from __future__ import annotations
import curses
import time
from abc import ABC, abstractmethod
# from game import Game  # cannot be used - circular import
from random import randint
from typing import Tuple, List, Set, Union


class GameEnded(Exception):
    pass


class Component(ABC):
    """
    Composite abstract class used to build other classes
    """

    def __init__(self, game):
        """
        Inits class Component
        :param game: Game instance passed by the game itself
        """
        self._game = game
        self._screen = game.screen
        self._settings = game.settings

    @property
    def game(self):
        return self._game

    @property
    def screen(self):
        return self._screen

    @property
    def settings(self):
        return self._settings

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
        :param color: A curses.colorpair-like object defining tile's appearance
        """
        super(Tile, self).__init__(game)
        self._chars = '  '
        self._typeface = color
        self._x, self._y = position

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, new_x):
        self._x = new_x

    @y.setter
    def y(self, new_y):
        self._y = new_y

    @property
    def position(self) -> Tuple[int, int]:
        """
        Returns tile's position on the board
        :return: Tile's position on the board
        """
        return self._x, self._y

    def draw(self, x_offset, y_offset, *args, **kwargs):
        """
        Draws the tile onto the screen, offsetting it by a given vector. Tiles are represented by two empty characters
        with a solid background places next to each other in order to correct for terminal font's rectangular glyph
        bounding boxes
        :param x_offset: X axis offset
        :param y_offset: Y axis offset
        :param args: Ignored
        :param kwargs: Ignored
        """
        try:
            self._screen.addstr(self._y + y_offset, 2 * self._x + x_offset, self._chars, self._typeface | curses.A_BOLD)
        except curses.error:
            pass  # uhhhhhhh this WILL cause errors

    def update(self, x: int, y: int):
        """
        Updates tile's position by a given offset
        :param x: X offset
        :param y: Y offset
        """
        self._x += x
        self._y += y


class BlockPreset(Component):  # NOT the best way to keep presets
    """
    Keeps all the information necessary for creating new blocks
    """

    def __init__(self, game, block_id, x):
        """
        Inits class BlockPreset
        :param game: Game instance passed by the game itself
        """
        super(BlockPreset, self).__init__(game)
        # ugly; block presets
        self._block_presets = (
            #       ####  0 cyan
            [(pos, 0) for pos in range(4)],
            #       #
            #       ####  1 blue
            [(pos, 1) for pos in range(3)] + [(0, 0)],
            #          #
            #       ####  2 orange
            [(pos, 1) for pos in range(3)] + [(2, 0)],
            #       ##
            #       ##  3 yellow
            [(0, 0), (0, 1), (1, 0), (1, 1)],
            #        ##
            #       ##   4 green
            [(1, 0), (2, 0), (0, 1), (1, 1)],
            #        #
            #       ###  5 magenta
            [(pos, 1) for pos in range(3)] + [(1, 0)],
            #        ##
            #       ##   6 red
            [(0, 0), (1, 0), (1, 1), (2, 1)]
        )
        self._color_presets = (curses.color_pair(11), curses.color_pair(12), curses.color_pair(13), curses.color_pair(
            14), curses.color_pair(15), curses.color_pair(16), curses.color_pair(17))

        # cyan block has a different pivot point
        self._pivot_point_presets = dict.fromkeys(list(range(1, 7)), [1 + x, 0])
        self._pivot_point_presets[0] = [1 + x, 1]

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """
        Updates the block's position
        :param args: Ignored
        :param kwargs: Ignored
        """
        super().update()

    @abstractmethod
    def draw(self, *args, **kwargs) -> None:
        """
        Draws the block onto the screen
        """
        super().draw()


class Block(BlockPreset):
    """
    Class representing a block of tiles. When the block is placed, tiles are moved to board.tiles and
    the class instance is deleted
    """

    def __init__(self, game, block_id: int):
        """
        Inits class Block
        :param game: Game instance passed by the game itself
        :param block_id: Indicates which block to spawn, block presets are stored in the superclass
        """
        super(Block, self).__init__(game, block_id, 0)
        self._id = block_id
        self._tiles = [Tile(self.game, (position[0], position[1]), self._color_presets[block_id])
                       for position in self._block_presets[block_id]]

        self._pivot_point = self._pivot_point_presets[block_id]

    @property
    def id(self):
        return self._id

    @property
    def tiles(self):
        return self._tiles

    @property
    def pivot_point(self):
        return self._pivot_point

    def update(self, x: int, y: int):
        """
        Updated the block's position by a given offset
        :param x: X offset
        :param y: Y offset
        """
        for tile in self._tiles:
            tile.update(x, y)

        self._pivot_point[0] += x
        self._pivot_point[1] += y

    def set_position(self, x: int, y: int) -> None:
        """
        Overrides block's position
        :param x: Target x axis position of the block's bounding box's upper left corner
        :param y: Target x axis position of the block's bounding box's upper left corner
        """
        current_x = min([tile.x for tile in self._tiles])
        current_y = min([tile.y for tile in self._tiles])
        for tile in self._tiles:
            tile.x -= current_x - x
            tile.y -= current_y - y

        self._pivot_point[0] -= current_x - x
        self._pivot_point[1] -= current_y - y

    def draw(self, x_offset: int, y_offset: int, *args, **kwargs):
        """
        Draws the block onto the screen, offsetting it by a given vector
        :param x_offset: X axis offset
        :param y_offset: Y axis offset
        :param args: Ignored
        :param kwargs: Ignored
        """
        for tile in self._tiles:
            tile.draw(x_offset, y_offset)

    def rotate(self, direction: int) -> None:
        """
        Rotates the block in the given direction
        :param direction: Indicates the direction, 1 for clockwise, -1 for counter-clockwise
        """
        # get new positions
        new_positions = self._get_rotated_positions(direction)

        # update the tiles with generated positions
        for tile_pos in zip(self._tiles, new_positions):
            tile_pos[0].x, tile_pos[0].y = tile_pos[1]

    def _get_rotated_positions(self, direction: int) -> List[Tuple[int, int]]:
        """
        Generates (x, y) pairs indicating the position in which the blocks will be after rotating
        the block in the given direction
        :param direction: Indicates the direction, 1 for clockwise, -1 for counter-clockwise
        :return: List of (x, y) pairs
        """
        p_x, p_y = self._pivot_point

        # cyan block rotates in a different way
        if self._id == 0:
            return [((p_y - tile.y) * direction + p_x, (p_x - tile.x) * direction + p_y)
                    for tile in self._tiles]
        else:
            return [((p_y - tile.y) * direction + p_x, (-p_x + tile.x) * direction + p_y)
                    for tile in self._tiles]

    def validate_rotation(self, direction: int) -> bool:
        """
        Checks if a rotation in the given direction can be performed
        :param direction: Indicates the direction, 1 for clockwise, -1 for counter-clockwise
        :return: True if the rotated block will overlap with another one or if it will be out
        of the board, False if it will
        """
        # yellow block does not rotate
        if self._id == 3:
            return False

        # get expected positions
        fields_to_check = self._get_rotated_positions(direction)

        # check if would overlap with other tiles or be placed out of the board
        return all(not self._game.board.get_tile(x, y)
                   and 0 <= x < self._game.board.size_x
                   and 0 <= y < self._game.board.size_y
                   for x, y in fields_to_check)

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

    def _get_fields_to_check(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Generates (self.x + x,self.y + y) pairs which will later be checked if they contain any obstacles
        :param x: X offset
        :param y: Y offset
        :return: A set of (x, y) pairs
        """
        return [(tile.x + x, tile.y + y) for tile in self._tiles]

    def _check_block_collisions(self, fields_to_check: List[Tuple[int, int]]) -> bool:
        """
        Checks for potential collision with other tiles
        :param fields_to_check: (x, y) pairs to be checked if they contain a tile
        :return: True if at least one of fields_to_check contains a tile, False if it does not
        """
        return any(bool(self._game.board.get_tile(x, y)) for x, y in fields_to_check)

    def _check_bottom_edge(self, fields_to_check: List[Tuple[int, int]]) -> bool:
        """
        Checks if the block sits at the board's bottom edge
        :param fields_to_check: (x, y) pairs to be checked if they are located below board's bottom edge
        :return: True if the block sits at the board's bottom edge, false if it does not
        """
        return any(self._game.board.get_tile(x, y, True) is True for x, y in fields_to_check)

    def _check_sides(self, fields_to_check: List[Tuple[int, int]]) -> bool:
        """
        Checks if the block is located next to the board's edge
        :param fields_to_check: (x, y) pairs to be checked if any of them is not located on the board
        :return: True if the block is located next to the board's edge, False if it's not
        """
        return any(field[0] < 0 or field[0] == self._game.board.size_x for field in fields_to_check)


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
        Handles horizontal movement on key press, moves the tile down or handles bottom collision if
        board.block_move_period passed
        :param board: Board class instance passed by the board itself
        :param key: Keyboard key id extracted by curses.getch
        """
        # handle horizontal movement
        key_mapping = {260: -1,
                       261: 1}
        x_direction = key_mapping.get(key, None)
        if x_direction and not board.block.check_side_collisions(x_direction):
            board.block.update(x_direction, 0)

        # handle rotation
        #         can also implement counter-clockwise rotation (with argument -1)
        if key == 259 and board.block.validate_rotation(1):
            board.block.rotate(1)

        # update vertical position every board.block_move_period
        if (time.time() - board.last_block_move) > board.block_move_period:
            if board.block.check_bottom_collisions():
                # handle collisions
                board.handle_bottom_collision()
            else:
                # move block down
                board.block.update(0, 1)
                board.last_block_move = time.time()


class HardDrop(BoardState):
    """
    Game state handling events if arrow down key was already pressed
    """

    @staticmethod
    def update(board: Board, key=None):
        """
        Calls board.handle_bottom_collision if a bottom collision is detected, moves the block down if it's not
        :param board: Board class instance passed by the board itself
        :param key: Ignored
        """
        if board.block.check_bottom_collisions():
            # handle bottom collisions
            board.handle_bottom_collision()
        else:
            # move the block down
            board.block.update(0, 1)
            board.last_block_move = time.time()


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

        # UI position
        self._position_x, self._position_y = (0, 0)

        # board size
        self._size_x = self.settings.BOARD_SIZE[0]
        self._size_y = self.settings.BOARD_SIZE[1]

        # tiles
        self._grid = [[None for _ in range(self._size_y)] for _ in range(self._size_x)]
        self._block = None
        self._next_block = Block(self.game, randint(0, 6))

        # timing
        self._block_move_period = game.settings.BLOCK_MOVEMENT_PERIOD
        self._last_block_move = time.time()

        # event handling
        self._soft_drop = SoftDrop()
        self._hard_drop = HardDrop()
        self._state = SoftDrop

    @property
    def block(self):
        return self._block

    @property
    def last_block_move(self):
        return self._last_block_move

    @property
    def block_move_period(self):
        return self._block_move_period

    @property
    def size_x(self):
        return self._size_x

    @property
    def size_y(self):
        return self._size_y

    @last_block_move.setter
    def last_block_move(self, new):
        self._last_block_move = new

    @property
    def tile_positions(self) -> List[Tuple[int, int]]:
        """
        Returns a position tuple for every tile on the board
        :return: A list of (x, y) tuples
        """
        return [tile.position for tile in self.tiles]

    @property
    def tiles(self) -> List[Union[Tile, None]]:
        """
        Returns all tiles on the board
        :return: A list of all Tile instances in self.tiles
        """
        # this will never return None, type checking errors should be ignored
        return [t for column in self._grid for t in column if t]

    def set_position(self, x: int, y: int) -> None:
        """
        Set board's absolute position on the screen
        :param x: X coordinate
        :param y: Y coordinate
        """
        self._position_x = x
        self._position_y = y

    def get_tile(self, x, y, default=None) -> Union[Tile, None]:
        """
        Similat to dict's method .get, tries to return the tile located at (x, y), returns default if there's none
        :param x: Tile's x coordinate
        :param y: Tile's y coordinate
        :param default: Value to be returned if there's no tile at (x, y)
        :return: A Tile instance or None / default
        """
        try:
            return self._grid[x][y]
        except IndexError:
            return default

    def draw(self) -> None:
        """
        Draws the board
        """
        # for tile in self.tiles:
        #     tile.draw(self._position_x, self._position_y)

        # added dotted background
        for column_idx in range(self._size_x):
            for row_idx in range(self._size_y):
                field = self._grid[column_idx][row_idx]
                if field:
                    field.draw(self._position_x, self._position_y)
                else:
                    self._screen.addch(row_idx + self._position_y, 2 * column_idx + self._position_x + 1, '.',
                                       curses.color_pair(10) | curses.A_BOLD)

        try:
            self._block.draw(self._position_x, self._position_y)
        except AttributeError:
            pass

    def update(self, key: int) -> None:
        """
        Controls tiles behavior
        :param key: Key code passed by curses.getch
        """

        if self._block:  # or try
            # switch do hard_drop on arrow down
            if key == 258:
                self._state = self._hard_drop
            else:
                self._state = self._soft_drop  # FIXME delayed response - should react to a key down event

            # handle user input, move the block, handle collisions
            self._state.update(self, key)

        else:  # or except AttributeError
            # spawn a new block
            self._state = self._soft_drop

            self._spawn_block(self._next_block)
            self._next_block = Block(self._game, randint(0, 6))

            self._game.ui.set_next_block(self._next_block)

    def _spawn_block(self, block: Block):
        self._block = block
        self._block.set_position(randint(0, 6), 0)
        # self.block.update(randint(0, 6), 0)

    def _add_to_grid(self, tiles: List[Tile]):
        for tile in tiles:
            self._grid[tile.x][tile.y] = tile  # FIXME ????

    def handle_bottom_collision(self) -> None:
        """
        Handles bottom collisions; moves the tiles from block.tiles to self.tiles, removes the full rows and
        deletes the block
        """

        if any(tile.y == 0 for tile in self.tiles):
            raise GameEnded

        # move tiles from block.tiles to self.tiles and delete the block object
        self._add_to_grid(self._block.tiles)

        # remove full rows and move the tiles down
        self._remove_full_rows()

        # delete the block
        self._block = None  # or del self.block

    def _remove_full_rows(self):
        """
        Checks if there are any full rows on the board and removes them
        """
        rows_to_delete = self._get_full_rows_idx({tile.y for tile in self._block.tiles})

        if rows_to_delete:

            # remove full rows
            for row in rows_to_delete:
                for column in self._grid:
                    del column[row]

                    # compensate for the deleted row
                    column.insert(0, None)

        # update tiles' attributes
        for tile in self.tiles:
            tile.update(0, sum(tile.y < row_idx for row_idx in rows_to_delete))

    def _get_full_rows_idx(self, to_check: Set[int]) -> List[int]:
        """
        Checks given rows and returns their indexes if they are full
        :param to_check: Indexes of rows that should be checked
        :return:
        """

        # build a list of tile.y coordinates
        tile_y = [tile.y for tile in self.tiles]

        # count the occurances and return the indexes
        return [idx for idx in to_check if tile_y.count(idx) == self._size_x]
