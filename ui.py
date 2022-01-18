from __future__ import annotations
from components import *
from abc import ABC, abstractmethod
from copy import copy
from typing import Sequence
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
                                  curses.color_pair(1),  # TODO check if the window is big enough for the game to run
                                  'Game')

        # stats window
        self._stats_frame = Frame(game, 4, 1, 19, 7,
                                  curses.color_pair(1),
                                  'Stats')
        self._score_titles = TextField(game, 6, 2, curses.color_pair(1), 'Score\n\nLines\n\nLevel')
        self._score_value = TextField(game, 6, 2, curses.color_pair(1), str(self._game.score).rjust(15))
        self._lines_value = TextField(game, 6, 4, curses.color_pair(1), str(self._game.cleared_lines).rjust(15))
        self._level_value = TextField(game, 6, 6, curses.color_pair(1), str(self._game.level).rjust(15))

        # next block window
        self._next_frame = Frame(game, 51, 1, 23, 6, curses.color_pair(1), 'Next')
        self._next_block = None
        self._next_block_position = (58, 4)

        # top scores
        self._top_scores_frame = Frame(game, 4, 9, 19, 12,
                                       curses.color_pair(1),
                                       'Scoreboard')
        self._top_scores_titles = TextField(game, 6, 10, curses.color_pair(1),
                                            '\n'.join([str(i) for i in range(1, 11)]))
        self._top_scores_values = TextField(game, 6, 10, curses.color_pair(1),
                                            '\n'.join([str(score).rjust(15) for score in self._game.scoreboard]))

        # controls
        self._controls_frame = Frame(game, 51, 8, 23, 9, curses.color_pair(1), 'Controls')
        self._controls_titles = TextField(game, 53, 9, curses.color_pair(1),
                                          'Left\nRight\nRotate\nSoft drop\nHard drop\nPause\nQuit')
        self._controls_keys = TextField(game, 65, 9, curses.color_pair(1),
                                        '←\n→\n↑\n↓\nspace\nesc\nq', align='right')

        # ####################################

        # game ended
        self._game_ended_box = Box(self._game, 24, 5, 26, 12, curses.color_pair(20))
        self._game_ended_frame = Frame(self._game, 24, 5, 26, 12, curses.color_pair(20))
        self._game_ended_message = TextField(self._game, 25, 7,
                                             curses.color_pair(1), 'you are not supposed to see this', align='center',
                                             width=24)

        # ####################################

        # paused
        self._paused_box = Box(self._game, 24, 8, 26, 7, curses.color_pair(20))
        self._paused_frame = Frame(self._game, 24, 8, 26, 7, curses.color_pair(20), 'Paused')
        self._paused_text = TextField(self._game, 25, 10, curses.color_pair(1),
                                      "space to resume\nesc to main menu\nq to quit", align='center', width=24)

        # ####################################

        # start menu

        tetris_title_text = ' _   _  ____ _______   _______ ______ _______ _____  _____  _____ \n'
        tetris_title_text += '| \ | |/ __ \__   __| |__   __|  ____|__   __|  __ \|_   _|/ ____|\n'
        tetris_title_text += '|  \| | |  | | | |       | |  | |__     | |  | |__) | | | | (___  \n'
        tetris_title_text += '| . ` | |  | | | |       | |  |  __|    | |  |  _  /  | |  \___ \ \n'
        tetris_title_text += '| |\  | |__| | | |       | |  | |____   | |  | | \ \ _| |_ ____) |\n'
        tetris_title_text += '|_| \_|\____/  |_|       |_|  |______|  |_|  |_|  \_\_____|_____/ '

        self._tetris_title = TextField(self._game, 3, 2, curses.color_pair(1), tetris_title_text)

        self._instructions_frame = Frame(self._game, 19, 10, 34, 7, curses.color_pair(1))
        self._instructions_text = TextField(self._game, 20, 11, curses.color_pair(1), 'Space to start\n\nQ to exit\n\n←  →  to choose starting level',
                                            align='center', width=32)

        self._starting_level_frame = Frame(self._game, 19, 17, 34, 3, curses.color_pair(1))
        self._starting_level_text = TextField(self._game, 20, 18, curses.color_pair(1), 'Starting level:   ', align='center', width=32)
        self._starting_level_value = TextField(self._game, 43, 18, curses.color_pair(2) | curses.A_BOLD, str(self._game.start_level))

        # ####################################

        # countdown

        self._countdown_box = Box(self._game, 25, 9, 24, 5, curses.color_pair(20))
        self._countdown_frame = Frame(self._game, 25, 9, 24, 5, curses.color_pair(20))
        self._countdown_text = TextField(self._game, 26, 10, curses.color_pair(1),
                                         "Get ready!\n\n3", align='center', width=22)

    @property
    def board_position(self):
        return self._board_position

    def set_blinking_score(self, flag: bool) -> None:
        """
        Makes the score blink or stops it blinking
        :param flag: A boolean value indicating if the score should be blinking
        """
        self._score_value.blinking = flag

    def reload_starting_level(self) -> None:
        """
        Reloads the starting level value
        """
        self._starting_level_value.text = str(self._game.start_level)

    def reload_scoreboard(self) -> None:
        """
        Reloads the scoreboard's contents
        """
        self._top_scores_values.text = '\n'.join(['{:>15}'.format(str(score)) for score in self._game.scoreboard])

    def reload_lines(self) -> None:
        """
        Reloads the cleared text counter
        """
        self._lines_value.text = '{:>15}'.format(str(self._game.cleared_lines))

    def reload_level(self) -> None:
        """
        Reloads the level counter
        :return:
        """
        self._level_value.text = '{:>15}'.format(str(self._game.level))

    def reload_score(self) -> None:
        """
        Reloads the score
        """
        self._score_value.text = '{:>15}'.format(str(self._game.score))

    def reload_next_block(self) -> None:
        """
        Places the next block to be spawned in self.next_block and corrects its position if needed
        """
        self._next_block = copy(self._game.board.next_block)
        if self._next_block.id == 0:
            self._next_block_position = (58, 4)
        elif self._next_block.id == 3:
            self._next_block_position = (60, 3)
        else:
            self._next_block_position = (59, 3)

    def reload_game_ended(self) -> None:
        """
        Updates the 'game over' message
        """
        score_msg = 'New high score' if self._game.new_high_score else 'Your score'
        msg = f'Game over!\n\n{score_msg}\n{self._game.score}\n\nspace to play again\nesc to main menu\nq to quit'
        self._game_ended_message.text = msg

    def reload_countdown(self) -> None:
        """
        Updates the countdown window
        """
        if self._game.countdown.ticks_to_start == 1:
            num = 'GO!'
        else:
            num = self._game.countdown.ticks_to_start - 1
        self._countdown_text.text = f"Get ready!\n\n{num}"

    def resize(self):
        """
        Resizes the terminal
        """
        is_resized = curses.is_term_resized(self._size_y, self._size_x)
        if is_resized:
            curses.resizeterm(self._size_y, self._size_x)

    def draw_board(self):  # TODO refactor to use a Drawable instance instead of all these methods
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
        try:
            self._next_block.draw(*self._next_block_position)
        except AttributeError:
            pass

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


class Drawable(ABC):
    """
    Base class used for creating UI components
    """

    def __init__(self, game):
        """
        Inits class Drawable
        :param game: A game class instance passed by the game itself
        """
        self._game = game

    @abstractmethod
    def draw(self) -> None:
        """
        Draws the object onto the screen
        """
        pass


#
# class Group(Drawable):
#     def __init__(self, game, items: Sequence[Drawable]):
#         super(Group, self).__init__(game)
#         self._items = items
#
#     @property
#     def items(self):
#         return self._items


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
        self._box.bkgd(' ', color | curses.A_BOLD)  # no need to use reverse
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
        :param x_pos: String's x coordinate
        :param y_pos: String's y coordinate
        :param color: A curses.colorpair-like object defining text's appearance
        :param text: A string meant do be displayed
        """
        super(TextField, self).__init__(game)

        self._x_position = x_pos
        self._y_position = y_pos
        self._color = color

        if not width:
            self._width = 0
        else:
            self._width = width
        self._align_mapping = {'left': 'ljust',
                               'center': 'center',
                               'right': 'rjust'}
        self._align = align

        self._lines = text.split(sep='\n')
        if not width:
            width = max([len(line) for line in self._lines])
        self._lines = eval(f'[line.{self._align_mapping[align]}({width}) for line in self._lines]')
        self._blinking = False

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
    def text(self, new_lines: str):
        self._lines = new_lines.split(sep='\n')
        # if self._align == 'center':
        #     self._width = max([len(line) for line in self._lines])
        self._lines = eval(f'[line.{self._align_mapping[self._align]}({self._width}) for line in self._lines]')

    def draw(self):
        """
        Draws the text onto the screen
        """
        for line_idx in range(len(self._lines)):
            self._game.screen.addstr(self._y_position + line_idx,
                                     self._x_position,
                                     self._lines[line_idx],
                                     self._color | (curses.A_BLINK if self._blinking else 1))
