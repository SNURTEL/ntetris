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
        self._game = game
        # self.size_y, self.size_x = game.screen.getmaxyx()  # TODO dynamic resize
        self._size_x, self._size_y = game.settings.WINDOW_SIZE

        # board
        # this is later called in Game class construction, cannot use board.set_position here, as it would require
        # referencing an object that's currently being initialized
        self._board_position = (27, 2)
        self._board_frame = Frame(game,
                                  self._board_position[0] - 1,
                                  self._board_position[1] - 1,
                                  2 * self._game.board.size_x + 2,
                                  self._game.board.size_y + 2,
                                  curses.color_pair(1),
                                  'Game')

        # stats window
        self._stats_frame = Frame(game, 4, 1, 19, 7,
                                  curses.color_pair(1),
                                  'Stats')
        self._score_titles = Text(game, 6, 2, curses.color_pair(1), 'Score\n\nLines\n\nLevel')
        self._score_value = Text(game, 6, 2, curses.color_pair(1), '{:>15}'.format(str(self._game.points)))
        self._lines_value = Text(game, 6, 4, curses.color_pair(1), '{:>15}'.format(str(self._game.cleared_lines)))
        self._level_value = Text(game, 6, 6, curses.color_pair(1), '{:>15}'.format(str(self._game.level)))

        # next block window
        self._next_frame = Frame(game, 51, 1, 23, 6, curses.color_pair(1), 'Next')
        self._next_block = None
        self._next_block_position = (58, 4)

        # top scores
        self._top_scores_frame = Frame(game, 4, 9, 19, 12,
                                       curses.color_pair(1),
                                       'Scoreboard')
        self._top_scores_titles = Text(game, 6, 10, curses.color_pair(1), '\n'.join([str(i) for i in range(1, 11)]))
        self._top_scores_values = Text(game, 6, 10, curses.color_pair(1),
                                       '\n'.join(['{:>15}'.format(str(score)) for score in self._game.scoreboard]))

        # controls
        self._controls_frame = Frame(game, 51, 8, 23, 8, curses.color_pair(1), 'Controls')
        self._controls_titles = Text(game, 53, 9, curses.color_pair(1),
                                     'Left\nRight\nRotate\nSoft drop\nHard drop\nQuit')
        self._controls_keys = Text(game, 65, 9, curses.color_pair(1),
                                   '←\n→\n↑\n↓\nspace\nq', align='right')

        # ####################################

        # game ended
        msg = 'Game ended'
        self._game_ended = Text(self._game, (self._size_x - len(msg)) // 2 + 1, (self._size_y - 1) // 2,
                                curses.color_pair(1), msg)

    @property
    def board_position(self):
        return self._board_position

    def set_blinking_score(self, flag: bool) -> None:
        """
        Makes the score blink or stops it blinking
        :param flag: A boolean value indicating if the score should be blinking
        """
        self._score_value.blinking = flag

    def reload_scoreboard(self) -> None:
        """
        Reloads the scoreboard's contents
        """
        self._top_scores_values.lines = '\n'.join(['{:>15}'.format(str(score)) for score in self._game.scoreboard])

    def reload_lines(self) -> None:
        """
        Reloads the cleared lines counter
        """
        self._lines_value.lines = '{:>15}'.format(str(self._game.cleared_lines))

    def reload_level(self) -> None:
        """
        Reloads the level counter
        :return:
        """
        self._level_value.lines = '{:>15}'.format(str(self._game.level))

    def reload_score(self) -> None:
        """
        Reloads the score
        """
        self._score_value.lines = '{:>15}'.format(str(self._game.points))

    def set_next_block(self, next_block: Block) -> None:
        """
        Places the next block to be spawned in self.next_block and corrects it's position if needed
        :param next_block:
        """
        self._next_block = copy(next_block)
        if self._next_block.id == 0:
            self._next_block_position = (58, 4)
        elif self._next_block.id == 3:
            self._next_block_position = (60, 3)
        else:
            self._next_block_position = (59, 3)

    def resize(self):
        """
        Resizes the terminal
        """
        is_resized = curses.is_term_resized(self._size_y, self._size_x)
        if is_resized:
            curses.resizeterm(self._size_y, self._size_x)

    def draw_board(self):
        """
        Draws the board
        """
        self._game.board.draw()
        self._board_frame.draw()

    def draw_stats(self):
        """
        Draws the stats window
        """
        self._stats_frame.draw()
        self._score_value.draw()
        self._lines_value.draw()
        self._level_value.draw()
        self._score_titles.draw()


    def draw_next(self):
        """
        Draws the next block window
        """
        self._next_frame.draw()
        self._next_block.draw(*self._next_block_position)

    def draw_top_scores(self):
        """
        Draws the top scores window
        """
        self._top_scores_frame.draw()
        self._top_scores_values.draw()
        self._top_scores_titles.draw()

    def draw_controls(self):
        """
        Draws the controls window
        """
        self._controls_frame.draw()
        self._controls_titles.draw()
        self._controls_keys.draw()

    def draw_game_ended(self):
        """
        Draws the 'game ended' message
        """
        self._game_ended.draw()


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
        self._game = game
        self._x_position = x
        self._y_position = y
        self._color = color

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
        self._x_len = x_len
        self._y_len = y_len

        # creates a subwindow
        self._box = self._game.screen.subwin(y_len, x_len, y_pos, x_pos)
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

        self._box = self._game.screen.subwin(y_len, x_len, y_pos, x_pos)
        self._box.idcok(False)
        self._box.idlok(False)

        self._title = Text(game, x_pos + (x_len - len(title)) // 2, y_pos, curses.color_pair(1), title)

    def draw(self) -> None:
        """
        Draws the frame onto the screen
        """
        self._box.border(0)
        self._title.draw()


class Text(Drawable):
    """
    A class representing a piece of text in the UI
    """

    def __init__(self, game, x_pos: int, y_pos: int, color, lines: str, align='left'):
        """
        Inits class Text
        :param game: A game class instance passed by the game itself
        :param x_pos: String's x coordinate
        :param y_pos: String's y coordinate
        :param color: A curses.colorpair-like object defining text's appearance
        :param lines: A string meant do be displayd
        """
        super(Text, self).__init__(game, x_pos, y_pos, color)
        self._lines = lines.split(sep='\n')
        self._align = align
        self._blinking = False

    @property
    def blinking(self):
        return self._blinking

    @blinking.setter
    def blinking(self, new_flag: bool):
        self._blinking = new_flag

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, new_lines: str):
        self._lines = new_lines.split(sep='\n')

    def draw(self):
        """
        Draws the text lines onto the screen
        """
        # don't look at this
        if self._align == "right":
            max_len = max(len(line) for line in self._lines)
            for line_idx in range(len(self._lines)):
                self._game.screen.addstr(self._y_position + line_idx,
                                         self._x_position + max_len - len(self._lines[line_idx]),
                                         self._lines[line_idx],
                                         self._color | (curses.A_BLINK if self._blinking else 1))
        else:
            for line_idx in range(len(self._lines)):
                self._game.screen.addstr(self._y_position + line_idx,
                                         self._x_position,
                                         self._lines[line_idx],
                                         self._color | (curses.A_BLINK if self._blinking else 1))
