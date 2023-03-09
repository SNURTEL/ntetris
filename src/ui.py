from __future__ import annotations

from components import *
from abc import ABC, abstractmethod
from copy import copy
from observers import Observer, Observable
import curses

from drawables import Drawable

class UI:
    def __init__(self, game):
        """
        Inits class UI
        :param game: A game class instance passed by the game itself
        """
        self._game = game
        self._size_x, self._size_y = game.settings.WINDOW_SIZE

        # board
        # this is later called in Game class construction, cannot use board.set_position here, as it would require
        # referencing an object that's currently being initialized
        self._board_position = (27, 2)
        self._board_frame = Frame(game,
                                  self._board_position[0] - 1,
                                  self._board_position[1] - 1,
                                  2 * game.board.size_x + 2,
                                  game.board.size_y + 2,
                                  curses.color_pair(1),
                                  'Game')

        # region views

        # stats window
        self._stats_frame = Frame(game, 4, 1, 19, 7,
                                  curses.color_pair(1),
                                  'Stats')
        self._score_titles = TextField(game, 6, 2, curses.color_pair(1), 'Score\n\nLines\n\nLevel')
        self._score_value = TextField(game, 6, 2, curses.color_pair(1), str(game.score), align='right', width=15)
        self._lines_value = TextField(game, 6, 4, curses.color_pair(1), str(game.cleared_lines), align='right',
                                      width=15)
        self._level_value = TextField(game, 6, 6, curses.color_pair(1), str(game.level), align='right', width=15)

        # next block window
        self._next_frame = Frame(game, 51, 1, 23, 6, curses.color_pair(1), 'Next')
        self._next_block = None
        self._next_block_position = (58, 4)  # Block.position should be used instead,
        # but I have no time to fix this lol

        # top scores
        self._top_scores_frame = Frame(game, 4, 9, 19, 12,
                                       curses.color_pair(1),
                                       title='Scoreboard')
        self._scoreboard = Scoreboard(game, 6, 10, 15, curses.color_pair(1), game.scoreboard)

        # controls
        self._controls_frame = Frame(game, 51, 8, 23, 9, curses.color_pair(1), 'Controls')
        self._controls_titles = TextField(game, 53, 9, curses.color_pair(1),
                                          'Left\nRight\nRotate\nSoft drop\nHard drop\nPause\nQuit')
        self._controls_keys = TextField(game, 65, 9, curses.color_pair(1),
                                        '←\n→\n↑\n↓\nspace\nesc\nq', align='right')

        # ####################################

        # game ended
        self._game_ended_box = Box(game, 24, 5, 26, 12, curses.color_pair(20))
        self._game_ended_frame = Frame(game, 24, 5, 26, 12, curses.color_pair(20))
        self._game_ended_message = GameEnded(game, 25, 7,
                                             curses.color_pair(1), 'you are not supposed to see this', align='center',
                                             width=24)

        # ####################################

        # paused
        self._paused_box = Box(game, 24, 8, 26, 7, curses.color_pair(20))
        self._paused_frame = Frame(game, 24, 8, 26, 7, curses.color_pair(20), 'Paused')
        self._paused_text = TextField(game, 25, 10, curses.color_pair(1),
                                      "space to resume\nesc to main menu\nq to quit", align='center', width=24)

        # ####################################

        # start menu

        tetris_title_text = ' _   _  ____ _______   _______ ______ _______ _____  _____  _____ \n'
        tetris_title_text += '| \\ | |/ __ \\__   __| |__   __|  ____|__   __|  __ \\|_   _|/ ____|\n'
        tetris_title_text += '|  \\| | |  | | | |       | |  | |__     | |  | |__) | | | | (___  \n'
        tetris_title_text += '| . ` | |  | | | |       | |  |  __|    | |  |  _  /  | |  \\___ \\ \n'
        tetris_title_text += '| |\\  | |__| | | |       | |  | |____   | |  | | \\ \\ _| |_ ____) |\n'
        tetris_title_text += '|_| \\_|\\____/  |_|       |_|  |______|  |_|  |_|  \\_\\_____|_____/ '

        self._tetris_title = TextField(game, 6, 2, curses.color_pair(1), tetris_title_text)

        self._instructions_frame = Frame(game, 22, 10, 34, 7, curses.color_pair(1))
        self._instructions_text = TextField(game, 23, 11, curses.color_pair(1),
                                            'Space to start\n\nQ to exit\n\n←  →  to choose starting level',
                                            align='center', width=32)

        self._starting_level_frame = Frame(game, 22, 17, 34, 3, curses.color_pair(1))
        self._starting_level_text = TextField(game, 23, 18, curses.color_pair(1), 'Starting level:   ',
                                              align='center', width=32)
        self._starting_level_value = TextField(game, 46, 18, curses.color_pair(2) | curses.A_BOLD,
                                               str(game.start_level))

        # ####################################

        # countdown

        self._countdown_box = Box(game, 25, 9, 24, 5, curses.color_pair(20))
        self._countdown_frame = Frame(game, 25, 9, 24, 5, curses.color_pair(20))
        self._countdown_text = Countdown(game, 26, 10, 22, curses.color_pair(1), 999)

        # window too small
        self._window_too_small = TextField(game, 0, 0, curses.color_pair(1), 'Window too small, please resize!',
                                           align='left')

        # endregion

        # additional observers
        self.next_block_observer = UI.NextBlockObserver(self)

        # observables
        self.window_size_observable = Observable(self, [self._window_too_small.text_observer])

    class NextBlockObserver(Observer):
        """
        Observer responsible for updating the next block preview
        """

        def update(self, observable, **kwargs):
            """
            Updates the next block
            :param observable: event caller
            :param kwargs: additional kwargs [blocks]
            """
            next_block = kwargs['block']
            self._outer._next_block = copy(next_block)
            self._outer._next_block.set_position(0, 0)
            block_id = next_block.id
            if block_id == 0:
                self._outer._next_block_position = (58, 4)
            elif block_id == 3:
                self._outer._next_block_position = (60, 3)
            else:
                self._outer._next_block_position = (59, 3)

    # region props

    @property
    def scoreboard(self):
        return self._scoreboard

    @scoreboard.setter
    def scoreboard(self, new_scores: list):
        self._scoreboard.text = new_scores

    @property
    def game_ended(self):
        return self._game_ended_message

    @game_ended.setter
    def game_ended(self, new_msg):
        self._game_ended_message.text = new_msg

    @property
    def next_block(self):
        return self._next_block

    @property
    def next_block_position(self):
        return self._next_block_position

    @next_block_position.setter
    def next_block_position(self, new_position: tuple):
        self._next_block_position = new_position

    @property
    def board_position(self):
        return self._board_position

    @property
    def starting_level(self):
        return self._starting_level_value

    @starting_level.setter
    def starting_level(self, new_level):
        self._starting_level_value.text = new_level

    @property
    def lines(self):
        return self._lines_value

    @lines.setter
    def lines(self, new_text):
        self._lines_value.text = new_text

    @property
    def score(self):
        return self._score_value

    @score.setter
    def score(self, new_score):
        self._score_value.text = new_score

    @property
    def level(self):
        return self._level_value

    @level.setter
    def level(self, new_level):
        self._level_value.text = new_level

    @property
    def countdown(self):
        return self._countdown_text

    @countdown.setter
    def countdown(self, new_text):
        self._countdown_text.text = new_text

    @property
    def blinking_score(self):
        return self._score_value.blinking

    @blinking_score.setter
    def blinking_score(self, flag: bool):
        """
        Makes the score blink or stops it blinking
        :param flag: A boolean value indicating if the score should be blinking
        """
        self._score_value.blinking = flag

    @property
    def window_too_small(self):
        y, x = self._game.screen.getmaxyx()
        return x < self._size_x or y < self._size_y

    # endregion

    def resize(self):
        """
        Resizes the terminal
        """
        is_resized = curses.is_term_resized(self._size_y, self._size_x)
        if not is_resized:
            return
        y, x = self._game.screen.getmaxyx()
        #  subwins truncate and cannot be resized back. No reason why
        if self.window_too_small:
            self.window_size_observable.set_changed(True)
            self.window_size_observable.notify(y=y - 1)

    # region draws

    def draw_window_too_small(self):
        try:
            self._window_too_small.draw()
        except curses.error:
            pass

    def draw_board(self):
        """
        Draws the board
        """
        self._game.board.draw(*self._board_position)
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
        try:
            self._next_block.draw(*self._next_block_position)
        except AttributeError:
            pass

    def draw_top_scores(self):
        """
        Draws the top scores window
        """
        self._top_scores_frame.draw()
        self._scoreboard.draw()

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
        self._game_ended_box.draw()
        self._game_ended_frame.draw()
        self._game_ended_message.draw()

    def draw_paused(self):
        """
        Draws the paused window onto the screen
        """
        self._paused_box.draw()
        self._paused_frame.draw()
        self._paused_text.draw()

    def draw_start_menu(self):
        """
        Draws the start menu onto the screen
        """
        self._tetris_title.draw()
        self._instructions_frame.draw()
        self._instructions_text.draw()

        self._starting_level_frame.draw()
        self._starting_level_text.draw()
        self._starting_level_value.draw()

    def draw_countdown(self):
        """
        Draws the countdown window onto the screen
        """
        self._countdown_box.draw()
        self._countdown_frame.draw()
        self._countdown_text.draw()

    # endregion





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
        super(Box, self).__init__(game)
        self._x_position = x_pos
        self._y_position = y_pos
        self._color = color

        self._x_len = x_len
        self._y_len = y_len

        # creates a subwindow
        self._box = self._game.screen.subwin(y_len, x_len, y_pos, x_pos)
        self._box.bkgd(' ', color | curses.A_BOLD)
        self._box.idcok(False)
        self._box.idlok(False)

    def draw(self) -> None:
        """
        Draws the box onto the screen
        """
        self._box.clear()


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
        super(Frame, self).__init__(game)

        self._x_position = x_pos
        self._y_position = y_pos
        self._color = color

        self.x_len = x_len
        self.y_len = y_len

        self._box = self._game.screen.subwin(y_len, x_len, y_pos, x_pos)
        self._box.idcok(False)
        self._box.idlok(False)

        if not title:
            title = ''

        self._title = TextField(game, x_pos + (x_len - len(title)) // 2, y_pos, curses.color_pair(1), title)

    def draw(self) -> None:
        """
        Draws the frame onto the screen
        """

        self._box.border(0)
        self._title.draw()


class TextField(Drawable):
    """
    A class representing a piece of text in the UI
    """

    def __init__(self, game, x_pos: int, y_pos: int, color, text: str, *, align='left', width=None, ):
        """
        Inits class TextField
        :param game: A game class instance passed by the game itself
        :param x_pos: TextField's x coordinate
        :param y_pos: TextField's y coordinate
        :param color: A curses.colorpair-like object defining text's appearance
        :param text: A string meant do be displayed
        :param align: Text's alignment [left/center/right]
        :param width: TextField's width
        """
        super(TextField, self).__init__(game)

        self._x_position = x_pos
        self._y_position = y_pos
        self._color = color

        if not width:
            self._width = 0
        else:
            self._width = width
        align_mapping = {'left': 'ljust',
                         'center': 'center',
                         'right': 'rjust'}
        self._align = align_mapping[align]

        self._lines = str(self._align_text(text, width)).split(sep='\n')

        self._blinking = False

        self.text_observer = TextField.TextFieldObserver(self)

    @property
    def x_position(self):
        return self._x_position

    @property
    def y_position(self):
        return self._y_position

    @x_position.setter
    def x_position(self, value: int):
        self._x_position = value

    @y_position.setter
    def y_position(self, value: int):
        self._y_position = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value: int):
        self._width = value

    class TextFieldObserver(Observer):
        """
        Special observer included with every TextField that allows to quickly update its contents
        """

        def update(self, observable, **kwargs):
            """
            Updates the text field
            :param observable: event caller
            :param kwargs: additional kwargs [text]
            """

            x, y, width, text = kwargs.get('x'), kwargs.get('y'), kwargs.get('width'), kwargs.get('text')

            if x is not None:
                self._outer.x_position = x
            if y is not None:
                self._outer.y_position = y
            if width is not None:
                self._outer.width = width
            if text is not None:
                self._outer.lines = text

    def _make_lines(self, text) -> list:
        """
        Converts the string into a list of properly aligned lines
        :param text: String to be processed
        """
        return self._align_text(text, self._width).split('\n')

    def _align_text(self, text, width: int = None) -> str:
        """
        Inserts empty chars to align lines in string
        :param text: String to be processed
        :param width: TextField width
        """
        if not width:
            width = self._get_max_width(text)
        return '\n'.join([line.__getattribute__(self._align)(width) for line in str(text).split('\n')])

    @staticmethod
    def _get_max_width(text: str) -> int:
        """
        Returns the maximum line length in the string
        :param text: String to be processed
        :return:
        """
        return max([len(line) for line in text.split('\n')])

    @property
    def blinking(self):
        return self._blinking

    @blinking.setter
    def blinking(self, new_flag: bool):
        self._blinking = new_flag

    @property
    def text(self):
        return self._lines

    @text.setter
    def text(self, new_text):
        self._lines = self._make_lines(str(new_text))

    def draw(self):
        """
        Draws the text onto the screen
        """
        for idx, line in enumerate(self._lines):
            self._game.screen.addstr(self._y_position + idx,
                                     self._x_position,
                                     line,
                                     self._color | (curses.A_BLINK if self._blinking else 1))


class Scoreboard(TextField):
    """
    A special TextField object with .text setter optimized for building the scoreboard
    """

    def __init__(self, game, x_pos: int, y_pos: int, width, color, scores: list):
        """
        Inits class Scoreboard
        :param game: A game class instance passed by the game itself
        :param x_pos: String's x coordinate
        :param y_pos: String's y coordinate
        :param width: Scoreboard's width
        :param color: A curses.colorpair-like object defining text's appearance
        :param scores: A list of scores
        """
        text = '\n'.join([f'{idx:<2}{score:>13}' for idx, score in zip(range(1, len(scores) + 1), scores)])
        super(Scoreboard, self).__init__(game, x_pos, y_pos, color, text, width=width)

    @property
    def text(self):
        return self._lines

    @text.setter
    def text(self, new_scores: list):
        self._lines = [f'{idx:<2}{score:>13}' for idx, score in zip(range(1, len(new_scores) + 1), new_scores)]


class Countdown(TextField):
    """
    A special TextField object with .text setter optimized for displaying the countdown window
    """

    def __init__(self, game, x_pos, y_pos, width, color, ticks_to_start):
        """
        Inits class Countdown
        :param game: A game class instance passed by the game itself
        :param x_pos: String's x coordinate
        :param y_pos: String's y coordinate
        :param width: TextField's width
        :param color: A curses.colorpair-like object defining text's appearance
        :param ticks_to_start: 'Ticks' left to start the game

        """
        text = ticks_to_start
        super(Countdown, self).__init__(game, x_pos, y_pos, color, text, align='center', width=width)

    @property
    def text(self):
        return self._lines

    @text.setter
    def text(self, ticks_to_start: int):
        if ticks_to_start == 1:
            num = 'GO!'
        else:
            num = ticks_to_start - 1
        text = f"Get ready!\n\n{num}"
        self._lines = self._make_lines(text)


class GameEnded(TextField):
    """
        A special TextField object with .text setter optimized for displaying the 'game over' message
    """

    def __init__(self, game, x_pos: int, y_pos: int, color, text: str, *, align='left', width=None):
        """
        Inits class GameEnded
        :param game: A game class instance passed by the game itself
        :param x_pos: TextField's x coordinate
        :param y_pos: TextField's y coordinate
        :param color: A curses.colorpair-like object defining text's appearance
        :param text: A string meant do be displayed
        :param align: Text's alignment [left/center/right]
        :param width: TextField's width
        """
        super(GameEnded, self).__init__(game, x_pos, y_pos, color, text, align=align, width=width)
        self.text_observer = GameEnded.GameEndedObserver(self)

    class GameEndedObserver(Observer):
        """
        A special Observer object used for updating the 'game over' message
        """

        def update(self, observable, **kwargs):
            score_msg = 'New high score' if kwargs['new_high_score'] else 'Your score'
            msg = f'Game over!\n\n{score_msg}\n{kwargs["score"]}\n\nspace to play again\nesc to main menu\nq to quit'
            self._outer.lines = msg
