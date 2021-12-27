from __future__ import annotations
from components import *
from abc import ABC, abstractmethod
from copy import copy
import curses


class UI:
    """Class managing game's UI"""

    def __init__(self, game):
        """
        Inits class UI
        :param game: A game class instance passed by the game itself
        """
        self.game = game
        # self.size_y, self.size_x = game.screen.getmaxyx()  # TODO dynamic resize
        self.size_x, self.size_y = game.settings.WINDOW_SIZE

        # board
        # this is later called in Game class construction, cannot use board.set_position here, as it would require
        # referencing an object that's currently being initialized
        self.board_position = (27, 2)
        self.board_frame = Frame(game,
                                 self.board_position[0] - 1,
                                 self.board_position[1] - 1,
                                 2 * self.game.board.size_x + 2,
                                 self.game.board.size_y + 2,
                                 curses.color_pair(1),
                                 'Game')

        # stats window
        self.stats_frame = Frame(game, 4, 1, 19, 5,
                                 curses.color_pair(1),
                                 'Stats')
        self.score_titles = Text(game, 6, 2, curses.color_pair(1), 'Score\n\nLevel')
        self.score_values = Text(game, 18, 2, curses.color_pair(1), 'XXX\n\nYYY')

        # next block window
        self.next_frame = Frame(game, 51, 1, 18, 6, curses.color_pair(1), 'Next')
        self.next_block = None
        self.next_block_position = (56, 4)

        # top scores
        self.top_scores_frame = Frame(game, 4, 7, 19, 12,
                                      curses.color_pair(1),
                                      'Stats')
        self.top_scores_titles = Text(game, 6, 8, curses.color_pair(1), '\n'.join([f"{i}." for i in range(1, 11)]))
        self.top_scores_values = Text(game, 18, 8, curses.color_pair(1),
                                           '\n'.join([str(111 * i) for i in reversed(range(1, 10))] + ['000']))

        # controls
        self.controls_frame = Frame(game, 51, 8, 18, 7, curses.color_pair(1), 'Controls')
        self.controls_titles = Text(game, 53, 9, curses.color_pair(1), 'Left\nRight\nRotate\nDrop\nQuit')
        self.controls_keys = Text(game, 66, 9, curses.color_pair(1),
                                       '←\n→\n↑\n↓\nq')

    def set_next_block(self, next_block: Block) -> None:
        """
        Places the next block to be spawned in self.next_block and corrects it's position if needed
        :param next_block:
        """
        self.next_block = copy(next_block)
        if self.next_block.id == 0:
            self.next_block_position = (56, 4)
        elif self.next_block.id == 3:
            self.next_block_position = (58, 3)
        else:
            self.next_block_position = (57, 3)

    def resize(self):
        """
        Resizes the terminal
        """
        is_resized = curses.is_term_resized(self.size_y, self.size_x)
        if is_resized:
            curses.resizeterm(self.size_y, self.size_x)

    def draw_board(self):
        """
        Draws the board
        """
        self.game.board.draw()
        self.board_frame.draw()

    def draw_stats(self):
        """
        Draws the stats window
        """
        self.stats_frame.draw()
        self.score_titles.draw()
        self.score_values.draw()

    def draw_next(self):
        """
        Draws the next block window
        """
        self.next_frame.draw()
        self.next_block.draw(*self.next_block_position)

    def draw_top_scores(self):
        """
        Draws the top scores window
        """
        self.top_scores_frame.draw()
        self.top_scores_titles.draw()
        self.top_scores_values.draw()

    def draw_controls(self):
        """
        Draws the controls window
        """
        self.controls_frame.draw()
        self.controls_titles.draw()
        self.controls_keys.draw()


class Drawable(ABC):
    """
    Base class used for creating UI components
    """

    def __init__(self, game, x: int, y: int, color):
        """
        Inits class Drawable
        :param game: A game class instance passed by the game itself
        :param x: Component's x coordinate
        :param y: Component's y coordinate
        :param color: A curses.colorpair-like object defining component's appearance
        """
        self.game = game
        self.x_position = x
        self.y_position = y
        self.color = color

    @abstractmethod
    def draw(self) -> None:
        """
        Draws the object onto the screen
        """
        pass


class Box(Drawable):
    """
    Class representing a solid fill box
    """

    def __init__(self, game, x_pos: int, y_pos: int, x_len: int, y_len: int, color):
        """
        Inits class box
        :param game: A game class instance passed by the game itself
        :param x_pos: Box's x coordinate
        :param y_pos: Box's y coordinate
        :param x_len: Box's horizontal length
        :param y_len: Box's vertical length
        :param color: A curses.colorpair-like object defining box's appearance
        """
        super(Box, self).__init__(game, x_pos, y_pos, color)
        self.x_len = x_len
        self.y_len = y_len

        # creates a subwindow
        self._box = self.game.screen.subwin(y_len, x_len, y_pos, x_pos)
        self._box.bkgd(' ', color | curses.A_BOLD | curses.A_REVERSE)  # no need to use reverse
        self._box.idcok(False)
        self._box.idlok(False)

    def draw(self) -> None:
        """
        Draws the box onto the screen
        """
        self._box.clear()  # TODO flicerking


class Frame(Drawable):
    """
    Class representing an outlined, transparent-fill box
    """

    def __init__(self, game, x_pos, y_pos, x_len, y_len, color, title=None):
        """
        Inits class frame
        :param game: A game class instance passed by the game itself
        :param x_pos: Frame's x coordinate
        :param y_pos: Frame's y coordinate
        :param x_len: Frame's horizontal length
        :param y_len: Frame's vertical length
        :param color: A curses.colorpair-like object defining frame's appearance
        :param title: (Optional) Frame's title, will be placed in frame's top part. Will crash if the title is too
        long to fit in the window
        """
        super(Frame, self).__init__(game, x_pos, y_pos, color)

        self.x_len = x_len
        self.y_len = y_len

        self._box = self.game.screen.subwin(y_len, x_len, y_pos, x_pos)
        self._box.idcok(False)
        self._box.idlok(False)

        self.title = Text(game, x_pos + (x_len - len(title)) // 2, y_pos, curses.color_pair(1), title)

    def draw(self) -> None:
        """
        Draws the frame onto the screen
        """
        self._box.border(0)
        self.title.draw()


class Text(Drawable):
    """
    A class representing a piece of text in the UI
    """

    def __init__(self, game, x_pos: int, y_pos: int, color, lines: str):
        """
        Inits class Text
        :param game: A game class instance passed by the game itself
        :param x_pos: String's x coordinate
        :param y_pos: String's y coordinate
        :param color: A curses.colorpair-like object defining text's appearance
        :param lines: A string meant do be displayd
        """
        super(Text, self).__init__(game, x_pos, y_pos, color)
        self.lines = lines.split(sep='\n')

    def draw(self):
        """
        Draws the text lines onto the screen
        """
        for line_idx in range(len(self.lines)):
            self.game.screen.addstr(self.y_position + line_idx, self.x_position, self.lines[line_idx], self.color)
