from __future__ import annotations
import curses
import time
from abc import ABC, abstractmethod
# from game import Game  # cannot be used - circular import
from random import randint
from typing import Tuple, List, Set, Union
from copy import copy

import keyboard


class GameEnded(Exception):
    """
    A custom exception indicating that the game has ended
    """
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
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @x.setter
    def x(self, new_x: int) -> None:
        self._x = new_x

    @y.setter
    def y(self, new_y: int) -> None:
        self._y = new_y

    @property
    def position(self) -> Tuple[int, int]:
        """
        Returns tile's position on the board
        :return: Tile's position on the board
        """
        return self._x, self._y

    def draw(self, x_offset: int, y_offset: int, *args, **kwargs):
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
            # print(self._y + y_offset, '####', 2 * self._x + x_offset)
            pass  # uhhhhhhh this WILL cause errors

    def update(self, x: int, y: int):
        """
        Updates tile's position by a given offset
        :param x: X offset
        :param y: Y offset
        """
        self._x += x
        self._y += y


class Block(Component):
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
        super(Block, self).__init__(game)

        # region block presets
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
        self._pivot_point_presets = dict.fromkeys(list(range(1, 7)), [1, 0])
        self._pivot_point_presets[0] = [1, 1]
        # endregion

        self._id = block_id
        self._tiles = [Tile(self.game, (position[0], position[1]), self._color_presets[block_id])
                       for position in self._block_presets[block_id]]

        self._pivot_point = self._pivot_point_presets[block_id]
        self._points = 0

    def __copy__(self) -> Block:
        """
        Shallow-copies all attributes and clones Tile instances in self._tiles to avoid unnecessary references
        This should be used instead of deepcopy, as it does not handle curses.window references very well
        :return: An identical Block instance
        """
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result.tiles = [copy(tile) for tile in self._tiles]
        return result

    @property
    def points(self) -> int:
        return self._points

    @property
    def id(self) -> int:
        return self._id

    @property
    def tiles(self) -> List[Tile]:
        return self._tiles

    @tiles.setter
    def tiles(self, new_tiles: List[Tile]):
        self._tiles = new_tiles

    @property
    def tile_positions(self) -> List[Tuple[int, int]]:
        return [(tile.x, tile.y) for tile in self._tiles]

    @property
    def pivot_point(self) -> Tuple[int, int]:
        return self._pivot_point  # u wot m8?

    def add_points(self, n: int) -> None:
        """
        Increases block's score
        :param n: number of score to be added
        """
        self._points += n

    def update(self, x: int, y: int) -> None:
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
        :param x: Target x-axis position of the block's bounding box's upper left corner
        :param y: Target y-axis position of the block's bounding box's upper left corner
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

        # check if the block would overlap with other tiles or be placed out of the board
        return self.validate_position(fields_to_check)

    def validate_position(self, fields_to_check: List[Tuple[int, int]]) -> bool:
        """
        Checks if any of the given fields overlaps with a block or is out of board's bounds
        :param fields_to_check: (x, y) pairs to be ckecked
        :return: Whether any of the given fields overlaps with a block or is out of board's bounds
        """
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
    def update(board: Board):
        """
        Moves the tiles and / or the current block and handles user input
        :param board: Board class instance passed by the board itself
        """
        pass


class Falling(BoardState):
    """
    Game state handling events if the down arrow key was not yet pressed
    """

    _last_block_move_x = time.time()
    _last_rotation = time.time()

    def update(self, board: Board):
        """
        Handles horizontal movement on key press, moves the tile down or handles bottom collision if
        board.block_move_period passed
        :param board: Board class instance passed by the board itself
        """
        # handle horizontal movement

        if time.time() - self._last_block_move_x > 0.088:
            if keyboard.is_pressed(105):
                x_direction = -1
            elif keyboard.is_pressed(106):
                x_direction = 1
            else:
                x_direction = 0

            # handle rotation
            #         can also implement counter-clockwise rotation (with argument -1)

            if x_direction and not board.block.check_side_collisions(x_direction):
                board.block.update(x_direction, 0)
                self._last_block_move_x = time.time()

        if keyboard.is_pressed(103) and time.time() - self._last_rotation > 0.2 and board.block.validate_rotation(1):
            board.block.rotate(1)
            self._last_rotation = time.time()

        # update vertical position every board.block_move_period
        if (time.time() - board.last_block_move_y) > board.block_move_period_y:
            board.block.update(0, 1)
            board.last_block_move_y = time.time()


class SoftDrop(BoardState):
    """
    Game state handling events if arrow down key was already pressed
    """

    @staticmethod
    def update(board: Board):
        """
        Calls board.handle_bottom_collision if a bottom collision is detected, moves the block down if it's not
        :param board: Board class instance passed by the board itself
        """
        if (time.time() - board.last_block_move_y) > board.block_move_period_y / 2\
                and not board.block.check_bottom_collisions():
            board.block.update(0, 1)
            board.last_block_move_y = time.time()
            board.block.add_points(1)

        if keyboard.is_pressed(57):
            board.state = board.hard_drop


class HardDrop(BoardState):
    """
    Game state handling events if the block is being hard dropped
    """

    @staticmethod
    def update(board: Board):
        """
        Moves the block down and adds score until it hits an obstacle
        :param board: A Board class instance passed by the board itself
        """
        while not board.block.check_bottom_collisions():
            board.block.update(0, 1)
            board.last_block_move_y = time.time()
            board.block.add_points(2)


class Board(Component):
    """
    Class representing a Tetris board
    """

    def __init__(self, game):
        """
        Inits class Board
        Dimensions are extracted from game's settings
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
        self._block_move_period = game.settings.BLOCK_MOVEMENT_PERIODS[0]
        self._last_block_move = time.time()
        self._space_already_pressed = False

        # event handling
        self.falling = Falling()
        self.soft_drop = SoftDrop()
        self.hard_drop = HardDrop()
        self.state = Falling

    @property
    def block(self):
        return self._block

    @property
    def last_block_move_y(self):
        return self._last_block_move

    @property
    def block_move_period_y(self):
        return self._block_move_period

    @block_move_period_y.setter
    def block_move_period_y(self, new: float):
        self._block_move_period = new

    @property
    def size_x(self):
        return self._size_x

    @property
    def size_y(self):
        return self._size_y

    @last_block_move_y.setter
    def last_block_move_y(self, new):
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

    @property
    def next_block(self):
        return self._next_block

    def reset_timings(self) -> None:
        """
        Resets Board's time - related attributes
        """
        self.last_block_move_y = time.time()

    def clear(self) -> None:
        """
        Clears the board
        """
        self._grid = [[None for _ in range(self._size_y)] for _ in range(self._size_x)]
        self._block = None

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
        Similar to Dict type's method .get, tries to return the tile located at (x, y), returns default if there's none
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

    def update(self) -> None:
        """
        Controls tiles behavior
        """
        # a.k.a. "The Great Mess"

        # switch do soft_drop on arrow down press
        if not self.block.check_bottom_collisions():
            if keyboard.is_pressed(57):
                if not self._space_already_pressed:
                    self.state = self.hard_drop
                    self._space_already_pressed = True

            elif keyboard.is_pressed(108):
                self.state = self.soft_drop

            # revert to falling on release
            else:
                self.state = self.falling
                self._space_already_pressed = False

            # handle user input, move the block, handle collisions aaa
            self.state.update(self)

        # handle collisions after a certain amount of time or if soft dropping
        elif (time.time() - self.last_block_move_y) > self.block_move_period_y * 0.4:
            self.handle_bottom_collision()

        # update the block if on top of another block
        elif self.state != self.hard_drop:
            self.state.update(self)

    def _load_next_block(self) -> None:
        """
        Sets the next block as current and generates a new one
        """
        self._block = copy(self._next_block)
        self._next_block = Block(self._game, randint(0, 6))

    def _spawn_block(self, block: Block) -> None:
        """
        Places the given block on the board
        :param block: A Block class instance, pre-generated for displaying in the UI
        """
        self._block = block
        self._block.set_position(randint(3, 5), 0)
        if not block.validate_position(self._block.tile_positions):
            del self._block
            raise GameEnded
        # self.block.update(randint(0, 6), 0)

    def _add_to_grid(self, tiles: List[Tile]) -> None:
        """
        Adds tiles to grid at their locations
        :param tiles: A list of tiles
        """
        for tile in tiles:
            self._grid[tile.x][tile.y] = tile  # pycharm u ok????

    def handle_bottom_collision(self) -> None:
        """
        Handles bottom collisions; moves the tiles from block.tiles to self.tiles, removes the full rows and
        deletes the block
        """
        # not a beauty

        # move tiles from block.tiles to self.tiles and delete the block object
        self._add_to_grid(self._block.tiles)

        # remove full rows and move the tiles down
        rows_to_delete = self._get_full_rows_idx({tile.y for tile in self._block.tiles})
        self._remove_full_rows(rows_to_delete)

        # add score
        # 100 single, 300 double, 500 triple, 800 tetris  # *(level+1)
        if rows_to_delete:
            self._game.add_points(
                (100 * (2 * len(rows_to_delete) - 1 + int(len(rows_to_delete) == 4))) * (self._game.level + 1))
        self._game.add_points(self._block.points)

        # add cleared text to counter
        self._game.add_lines(len(rows_to_delete))

        # increment level
        if self._game.cleared_lines >= 10 * (self._game.level + 1):
            self.game.level_up()

        # load a new block and generate the next one
        self._spawn_block(self._next_block)
        self._load_next_block()

        # switch states
        self.state = self.falling

    def _remove_full_rows(self, rows_to_delete: List[int]):
        """
        Checks if there are any full rows on the board and removes them
        """
        if rows_to_delete:

            # remove full rows
            for row in sorted(rows_to_delete):
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

        # count the occurrences and return the indexes
        return [idx for idx in to_check if tile_y.count(idx) == self._size_x]

    def new_game(self):
        """
        Clears the board and generates new blocks
        :return:
        """
        self.clear()
        new_block = Block(self._game, randint(0, 6))
        self._spawn_block(new_block)
        self._next_block = Block(self._game, randint(0, 6))
