from __future__ import annotations

import curses
import sys

import keyboard

import argparse
import time
import json

from settings import Settings
from components import Board, GameEnded
from observers import Observable, Observer
from abc import ABC, abstractmethod
from ui import UI
from typing import List


class GameState(ABC):
    """
    Composite abstract class used to build GameStates
    """

    def __init__(self, game: Game):
        """
        Inits class GameState
        :param game: Game instance passed by the game itself
        """
        self._game = game
        self._settings = self._game.settings

        self._observables = []

    @abstractmethod
    def greet(self) -> None:
        """
        Method called every time games switches to the state
        :return:
        """
        pass

    @abstractmethod
    def notify_observers(self):
        """
        Notifies the observers associated with the state and the corresponding UI elements
        """
        pass

    @property
    def game(self) -> Game:
        return self._game

    @property
    def settings(self) -> Settings:
        return self._settings

    @abstractmethod
    def handle_events(self) -> None:
        """
        Handles events in a unique way for every GameState
        """
        pass

    @abstractmethod
    def update_screen(self) -> None:
        """
        Draws the game in a unique way for every GameState
        """
        pass


class Active(GameState):
    """
    Active state of the game
    """

    def greet(self):
        self._game.reset_timings()

    def handle_events(self) -> None:
        """
        Reads keyboard input, updates the board and the UI
        """
        try:
            if keyboard.is_pressed(16):
                sys.exit()
            elif keyboard.is_pressed(1):
                self._game.switch_to_state(Paused)
            else:
                self._game.board.update()
        except GameEnded:

            self._game.switch_to_state(Ended)

    def update_screen(self) -> None:
        """
        Draws the board and the UI
        """

        self._game.ui.draw_board()
        self._game.ui.draw_stats()
        self._game.ui.draw_next()
        self._game.ui.draw_top_scores()
        self._game.ui.draw_controls()

    def notify_observers(self):
        """
        Notifies gameplay-related observers marked with flag 'changed'
        """
        self._game.score_observable.notify(text=self.game.score)
        self._game.lines_observable.notify(text=self.game.cleared_lines)
        self._game.level_observable.notify(text=self.game.level)
        self._game.next_block_observable.notify(block=self.game.board.next_block)
        self._game.scoreboard_observable.notify(text=self.game.scoreboard)


class Ended(GameState):
    """
    Ended state of the game
    """

    _space_already_pressed = False

    def greet(self) -> None:
        """
        Prepares the scoreboard for display
        """
        self._game.update_scoreboard()
        self._game.ui.blinking_score = False

        self._game.score_observable.set_changed(True)
        self._game.scoreboard_observable.set_changed(True)
        self._game.game_ended_observable.set_changed(True)

        self._space_already_pressed = True

    def notify_observers(self):
        """
        Notifies score-related observers marked with flag 'changed'
        """
        self._game.game_ended_observable.notify(new_high_score=self._game.new_high_score, score=self._game.score)
        self._game.scoreboard_observable.notify(text=self.game.scoreboard)

    def handle_events(self) -> None:
        """
        Handles UI navigation, does not update the board
        """
        if keyboard.is_pressed(16):
            sys.exit()
        elif keyboard.is_pressed(57):
            if not self._space_already_pressed:
                self._game.prep_for_new_game()
                self._game.switch_to_state(Countdown)
                self._space_already_pressed = True

        elif keyboard.is_pressed(1):
            self._game.switch_to_state(StartMenu)
        else:
            self._space_already_pressed = False

    def update_screen(self) -> None:
        """
        Draws the board and the UI
        """
        # this can all be moved to greet

        self._game.ui.draw_board()
        self._game.ui.draw_stats()
        self._game.ui.draw_next()
        self._game.ui.draw_top_scores()
        self._game.ui.draw_controls()

        self._game.ui.draw_game_ended()


class Paused(GameState):
    """
    Paused state of the game
    """

    _esc_already_pressed = True

    def greet(self) -> None:
        """
        This state can only be entered with the esc key
        :return:
        """
        self._esc_already_pressed = True

    def handle_events(self):
        """
        Waits for user input and reverts the game back to Active, or quits it
        """

        if keyboard.is_pressed(1) and self._esc_already_pressed:
            return

        if keyboard.is_pressed(16):
            sys.exit()
        elif keyboard.is_pressed(57):
            self._game.switch_to_state(Countdown)
        elif keyboard.is_pressed(1):
            self._game.update_scoreboard()
            self._game.switch_to_state(StartMenu)
        else:
            self._esc_already_pressed = False

    def update_screen(self) -> None:
        """
        Updates the screen
        """

        self._game.ui.draw_board()
        self._game.ui.draw_stats()
        self._game.ui.draw_next()
        self._game.ui.draw_top_scores()
        self._game.ui.draw_controls()

        self._game.ui.draw_paused()

    def notify_observers(self):
        pass


class StartMenu(GameState):
    """
    GameS=tate used for managing navigation around the main menu and starting the game
    """
    _last_update = time.time()

    def greet(self) -> None:
        """
        Sets game's starting level to 0
        """
        self._last_update = time.time()
        self._game.start_level = 0
        self._game.starting_level_observable.set_changed(True)

    def handle_events(self) -> None:
        """
        Handles keypresses
        """

        if time.time() - self._last_update < 0.1:
            return

        if keyboard.is_pressed(16):
            sys.exit()
        elif keyboard.is_pressed(57):
            self._game.prep_for_new_game()
            self._game.switch_to_state(Countdown)
            self._last_update = time.time()
        elif keyboard.is_pressed(105) and self._game.start_level > 0:
            self._game.start_level -= 1
            self._game.starting_level_observable.set_changed(True)
            self._last_update = time.time()

        elif keyboard.is_pressed(106) and self._game.start_level < 29:
            self._game.start_level += 1
            self._game.starting_level_observable.set_changed(True)
            self._last_update = time.time()

    def update_screen(self) -> None:
        """
        Draws the menu
        """
        self._game.screen.erase()

        self._game.ui.draw_start_menu()

        self._game.screen.refresh()

    def notify_observers(self):
        """
        Notifies the starting level observer (if marked with flag 'changed')
        """
        self._game.starting_level_observable.notify(text=self.game.start_level)


class Countdown(GameState):
    """
    GameState used to wait X seconds before the game runs
    """
    _ticks_to_start = 4
    _last_update = time.time()

    def greet(self) -> None:
        """
        Resets the timing-related attributes and reloads the UI
        """
        self._ticks_to_start = 4

        self._game.countdown_observable.set_changed(True)
        self._game.score_observable.set_changed(True)
        self._game.level_observable.set_changed(True)

        self._last_update = time.time()

    def handle_events(self) -> None:
        """
        Updates the UI every Y seconds, switches to Active after a few ticks; quits the game on q
        """

        if keyboard.is_pressed(16):
            sys.exit()

        if time.time() - self._last_update > 0.55:
            self._ticks_to_start -= 1
            self._last_update = time.time()
            self._game.countdown_observable.set_changed(True)

        if self._ticks_to_start == 0:
            self.game.switch_to_state(Active)

    def update_screen(self) -> None:
        """
        Draws the board and the countdown window
        """

        self._game.ui.draw_board()
        self._game.ui.draw_stats()
        self._game.ui.draw_next()
        self._game.ui.draw_top_scores()
        self._game.ui.draw_controls()

        self._game.ui.draw_countdown()

    def notify_observers(self):
        """
        Notifies countdown and block observers'
        """
        self._game.countdown_observable.notify(text=self.game.countdown.ticks_to_start)
        self._game.next_block_observable.notify(block=self._game.board.next_block)
        self._game.score_observable.notify(text=self._game.score)
        self._game.scoreboard_observable.notify(text=self._game.scoreboard)
        self._game.level_observable.notify(text=self._game.level)

    @property
    def ticks_to_start(self):
        return self._ticks_to_start


class WindowTooSmall(GameState):
    """
    GameState used for indicating that the window should be resized
    """

    def greet(self) -> None:
        pass

    def update_screen(self) -> None:
        """
        Draws the message
        """
        self._game.screen.erase()
        self._game.ui.draw_window_too_small()
        self._game.screen.refresh()

    def handle_events(self) -> None:
        """
        Checks if the window has been resized
        """
        if not self._game.ui.window_too_small:
            self._game.revert_state()

    def notify_observers(self):
        pass


class Game:
    """
    Main class representing a Tetris game. Settings are loaded from settings.py #
    """

    def __init__(self, screen: curses.window):
        """
        Inits class game
        :param screen: curses.window instance passed by the wrapper
        """

        # components
        self._settings = Settings()
        self._screen = screen
        self._screen.timeout(0)
        curses.cbreak()  # does nothing
        self._board = Board(self)

        # scoring
        self._start_level = 0

        self._level = 0
        self._points = 0
        self._cleared_lines = 0

        self._scoreboard_filename = self._settings.SCOREBOARD_FILENAME
        self._scoreboard = self._load_scoreboard(self._scoreboard_filename)

        # managing states
        self._active = Active(self)
        self._ended = Ended(self)
        self._paused = Paused(self)
        self._start_menu = StartMenu(self)
        self._countdown = Countdown(self)
        self._window_too_small = WindowTooSmall(self)

        self._state = self._ended
        self._previous_state = self._start_menu

        # UI
        curses.curs_set(False)
        try:
            self._ui = UI(self)
        except curses.error:
            curses.endwin()
            print('Window too small, please resize!')
            sys.exit()

        self._screen.idcok(False)  # use if flickering appears
        self._screen.idlok(False)

        # cannot be done in UI class constructor
        self._board.set_position(*self._ui.board_position)

        # timing
        self._start_time = time.time()
        self._refresh_period = 1.0 / self._settings.REFRESH_RATE
        self._last_screen_update = time.time()
        self._block_movement_periods = self._settings.BLOCK_MOVEMENT_PERIODS

        # load default terminal colors
        curses.use_default_colors()

        # init custom colors
        for idx, rgb in self._settings.CUSTOM_COLORS.items():
            curses.init_color(idx, *rgb)

        # init color pairs
        for idx, rgb in self._settings.COLOR_PAIRS.items():
            curses.init_pair(idx, *rgb)

        # observers

        self.window_size_observer = self.WindowSizeObserver(self)
        self.ui.window_size_observable.attach_observer(self.window_size_observer)

        # observables
        self.score_observable = Observable(self, [self.ui.score.text_observer])
        self.lines_observable = Observable(self, [self.ui.lines.text_observer])
        self.level_observable = Observable(self, [self.ui.level.text_observer])
        self.scoreboard_observable = Observable(self, [self.ui.scoreboard.text_observer])
        self.countdown_observable = Observable(self, [self.ui.countdown.text_observer])
        self.starting_level_observable = Observable(self, [self.ui.starting_level.text_observer])
        self.game_ended_observable = Observable(self, [self.ui.game_ended.text_observer])
        self.next_block_observable = Observable(self, [self.ui.next_block_observer])

    # region props

    @property
    def state(self):
        return self._state

    @property
    def new_high_score(self):
        return self._points >= self._scoreboard[0]

    @property
    def start_level(self):
        return self._start_level

    @start_level.setter
    def start_level(self, new: int):
        self._start_level = new

    @property
    def countdown(self):
        return self._countdown

    @property
    def scoreboard(self):
        return self._scoreboard

    @property
    def score(self):
        return self._points

    @property
    def level(self):
        return self._level

    @property
    def ui(self):
        return self._ui

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def screen(self) -> curses.window:
        return self._screen

    @property
    def board(self) -> Board:
        return self._board

    @property
    def period(self):
        return self._refresh_period

    @property
    def cleared_lines(self):
        return self._cleared_lines

    # endregion

    class WindowSizeObserver(Observer):
        def update(self, observable, **kwargs):
            if not type(self._outer.state) == WindowTooSmall:
                self._outer.switch_to_state(WindowTooSmall)

    def level_up(self) -> None:
        """
        Increments the level by 1 and reloads parts of the UI responsible for displaying it; increases game's speed
        :return:
        """
        self._level += 1
        self.level_observable.set_changed(True)
        self._board.block_move_period_y = self._get_speed(self._level)

    def _get_speed(self, level: int) -> float:
        """
        Finds the adequate update period for the level
        :param level: Current game's level
        :return:
        """
        new_speed = None
        while not new_speed:
            new_speed = self._block_movement_periods.get(level)
            level -= 1

        return new_speed

    def add_lines(self, n: int) -> None:
        """
        Increments the cleared text counter  and reloads parts of the UI responsible for displaying it
        :param n: A number of cleared text to be added
        """
        self._cleared_lines += n
        self.lines_observable.set_changed(True)

    def prep_for_new_game(self, level: int = 0) -> None:
        """
        Resets game's score and timing related attributes and sets the starting level
        :param level: Override self._start_level
        """
        if level:
            self._start_level = level
        self._level = self._start_level
        self._board.block_move_period_y = self._get_speed(self._start_level)
        self._points = 0
        self._cleared_lines = 0
        self._start_time = time.time()

        self.board.new_game()

        self.score_observable.set_changed(True)
        self.lines_observable.set_changed(True)
        self.level_observable.set_changed(True)
        self.scoreboard_observable.set_changed(True)
        self.next_block_observable.set_changed(True)

    def reset_timings(self) -> None:
        """
        Resets game's timing-related attributes
        """
        self._last_screen_update = time.time()
        self._board.reset_timings()

    def add_points(self, n: int) -> None:
        """
        Adds score to the counter and starts flashing it if a new high score has been set; reloads the UI score
        :param n: the number of score to be added
        :return:
        """
        self._points += n
        if self.new_high_score:
            self.ui.blinking_score = True
        self.score_observable.set_changed(True)
        self.next_block_observable.set_changed(True)

    def update_scoreboard(self) -> None:
        """
        Writes the score to the scoreboard if it's in the top 10
        """
        points = self._points
        if points >= self._scoreboard[-1] and points not in self._scoreboard:
            for i in range(len(self._scoreboard)):
                if self._scoreboard[i] < points:
                    self._scoreboard.insert(i, points)
                    del self._scoreboard[-1]
                    self._save_scoreboard(self._scoreboard)
                    return

    def switch_to_state(self, state) -> None:
        """
        Switches the game to the given state
        :param state: The next gamestate
        """

        state_mapping = {
            Active: self._active,
            Ended: self._ended,
            Paused: self._paused,
            StartMenu: self._start_menu,
            Countdown: self._countdown,
            WindowTooSmall: self._window_too_small
        }

        self._previous_state = self._state
        self._state = state_mapping[state]
        self._state.greet()

    def revert_state(self):
        self._state = self._previous_state

    def _save_scoreboard(self, scoreboard: List[int]) -> None:
        """
        Saves the scoreboard to a json file
        :param scoreboard: The scoreboard to be saved
        """
        with open(self._scoreboard_filename, mode='w', encoding='utf-8') as fp:
            self._write_scoreboard(fp, scoreboard)

    def _clear_scoreboard(self, filename: str):
        empty_sb = [0 for _ in range(10)]
        with open(filename, mode='w', encoding='utf-8') as fp:
            self._write_scoreboard(fp, empty_sb)
        self._scoreboard = empty_sb

    @staticmethod
    def _write_scoreboard(fp, scoreboard) -> None:
        """
        Writes the scoreboard to json using the given fp
        :param fp: A file handle in 'w' mode
        :param scoreboard: The scoreboard to be written
        """
        json.dump({'scoreboard': scoreboard}, fp, indent=4)

    def _load_scoreboard(self, filename: str) -> List[int]:
        """
        Recreates the scoreboard from the json file
        :param filename:
        :return: The recreated scoreboard
        """
        try:
            with open(filename, mode='r', encoding='utf-8') as fp:
                scoreboard = sorted(self._read_scoreboard(fp), reverse=True)
        except FileNotFoundError:
            scoreboard = [0 for _ in range(10)]
            self._save_scoreboard(scoreboard)
        return scoreboard

    @staticmethod
    def _read_scoreboard(fp) -> List[int]:
        """
        Reads the scoreboard from the json file
        :param fp: A file handle in 'r' mode
        :return: The recreated scoreboard
        """
        return json.load(fp)['scoreboard']

    def _wait_till_next_tick(self) -> None:
        """
        Ensures that 1s/refresh rate passes between every event loop iteration
        """
        time.sleep(self._refresh_period - ((time.time() - self._start_time) % self._refresh_period))

    def run_game(self) -> None:
        """
        Starts the game
        """

        parser = argparse.ArgumentParser()
        parser.add_argument("--level", help="set starting level")
        parser.add_argument('--clear-scoreboard', action='store_true', help='clear the scoreboard')
        args = parser.parse_args()

        if args.clear_scoreboard:
            self._clear_scoreboard('scoreboard.json')
            self.score_observable.set_changed(True)

        if args.level:
            # skip the menu and start the game at the specified level
            self.prep_for_new_game(int(args.level))
            self.switch_to_state(Countdown)
        else:
            # start through main menu
            self.switch_to_state(StartMenu)

        #  main event loop
        try:
            while True:
                try:
                    # terminal resize handling
                    self._ui.resize()

                    # game's logic
                    self._state.handle_events()

                    # ui updates
                    self._state.notify_observers()

                    # screen re-drawing
                    self._screen.erase()
                    self._state.update_screen()
                    self._screen.refresh()

                    # timing
                    self._last_screen_update = time.time()
                    self._wait_till_next_tick()

                except KeyboardInterrupt:
                    # ignore
                    continue
        except ImportError:
            curses.endwin()
            print('Due to the keypress registering limitation in Linux, the game must be run with root privileges.')
            sys.exit()
        except AssertionError:
            curses.endwin()
            print('Keyboard not found!')

        finally:
            # on sys.exit
            self.update_scoreboard()
            curses.endwin()

            # does not work. lol
            # keyboard.call_later((lambda: keyboard.send('ctrl+u')), delay=0.05)
