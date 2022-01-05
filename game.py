from __future__ import annotations
import curses
import time
import sys
import json
from settings import Settings
from components import Board, GameEnded
from abc import ABC, abstractmethod
from ui import UI
from typing import Type, List


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

    @abstractmethod
    def greet(self) -> None:
        """
        Method called every time games switches to the state
        :return:
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

    #  what about __init__? Seems to work just fine without it...

    def greet(self):
        self._game.reset()

    def handle_events(self) -> None:
        """
        Reads keyboard input, updates the board and the UI
        """
        try:
            key = self._game.screen.getch()
            if key == 113:
                sys.exit()
            else:
                self._game.board.update(key)
        except GameEnded:
            self._game.switch_to_state(Ended)

    def update_screen(self) -> None:
        """
        Draws the board and the UI
        """

        self._game.screen.erase()

        self._game.ui.draw_board()
        self._game.ui.draw_stats()
        self._game.ui.draw_next()
        self._game.ui.draw_top_scores()
        self._game.ui.draw_controls()

        self._game.screen.refresh()


class Ended(GameState):
    """
    Ended state of the game
    """

    def greet(self) -> None:
        """
        Prepares the scoreboard for display
        """
        self._game.update_scoreboard(self._game.points)
        self._game.ui.set_blinking_score(False)
        self._game.ui.reload_scoreboard()

    def handle_events(self) -> None:
        """
        Handles UI navigation, does not update the board
        """
        key = self._game.screen.getch()

        if key == 113:
            sys.exit()

    def update_screen(self) -> None:
        """
        Draws the board and the UI
        """
        self._game.ui.draw_game_ended()
        self._game.ui.draw_stats()
        self._game.ui.draw_top_scores()

        self._game.screen.refresh()


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
        self._level = 0
        self._points = 0
        self._cleared_lines = 0

        self._scoreboard_filename = self._settings.SCOREBOARD_FILENAME
        self._scoreboard = self._load_scoreboard(self._scoreboard_filename)

        # managing states
        self._active = Active(self)
        self._ended = Ended(self)

        self._state = self._ended

        # UI
        curses.curs_set(False)
        self._ui = UI(self)

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

    @property
    def scoreboard(self):
        return self._scoreboard

    @property
    def points(self):
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

    def level_up(self) -> None:
        """
        Increments the level by 1 and reloads parts of the UI responsible for displaying it; increases game's speed
        :return:
        """
        self._level += 1
        self.ui.reload_level()
        new_speed = self._block_movement_periods.get(self._level)
        if new_speed:
            self._board.block_move_period = new_speed

    def add_lines(self, n: int) -> None:
        """
        Increments the cleared lines counter  and reloads parts of the UI responsible for displaying it
        :param n: A number of cleared lines to be added
        """
        self._cleared_lines += n
        self.ui.reload_lines()

    def reset(self) -> None:
        """
        Resets current game's stats
        """
        self._level = 0
        self._points = 0
        self._cleared_lines = 0

    def add_points(self, n: int) -> None:
        """
        Adds points to the counter and starts flashing it if a new high score has been set; reloads the UI score
        :param n: the number of points to be added
        :return:
        """
        self._points += n
        if self._points >= self._scoreboard[0]:
            self.ui.set_blinking_score(True)
        self._ui.reload_score()


    def update_scoreboard(self, points: int) -> None:
        """
        Writes the score to the scoreboard if it's in the top 10
        :param points: The score that needs to be checked and, if applicable, written
        """
        if points >= self._scoreboard[-1] and points not in self._scoreboard:
            for i in range(len(self._scoreboard)):
                if self._scoreboard[i] < points:
                    self._scoreboard.insert(i, points)
                    del self._scoreboard[-1]
                    self._save_scoreboard(self._scoreboard)
                    return

    def switch_to_state(self, state: Type[GameState]) -> None:
        """
        Switches the game to the given state
        :param state: The next gamestate
        """

        state_mapping = {
            Active: self._active,
            Ended: self._ended
        }

        self._state = state_mapping[state]
        self._state.greet()

    def _save_scoreboard(self, scoreboard: List[int]) -> None:
        """
        Saves the scoreboard to a json file
        :param scoreboard: The scoreboard to be saved
        """
        with open(self._scoreboard_filename, mode='w', encoding='utf-8') as fp:
            self._write_scoreboard(fp, scoreboard)

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
        self.switch_to_state(Active)
        self._start_time = time.time()

        #  main event loop
        try:
            while True:
                try:
                    self._state.handle_events()

                    self._state.update_screen()
                    self._ui.resize()
                    self._last_screen_update = time.time()

                    self._wait_till_next_tick()
                except KeyboardInterrupt:
                    # ignore
                    continue
        finally:
            # on sys.exit
            self.update_scoreboard(self._points)
            curses.endwin()
            print(':D')
