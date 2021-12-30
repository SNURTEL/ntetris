from __future__ import annotations
import curses
import time
import sys
from settings import Settings
from components import Board, GameEnded
from abc import ABC, abstractmethod
from ui import UI
from typing import Type


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

    def handle_events(self) -> None:
        """
        Handles UI navigation, does not update the board
        """
        pass  # call update method on every component

    def update_screen(self) -> None:
        """
        Draws the board and the UI
        """
        # self._game.screen.erase()

        self._game.ui.draw_game_ended()
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

        self._board = Board(self)

        # managing states
        self._active = Active(self)
        self._ended = Ended(self)

        self._state = self._ended

        # UI
        curses.curs_set(False)
        self._ui = UI(self)

        self._screen.idcok(False)  # use if flickering appears
        self._screen.idlok(False)

        # cannot be done in UI class constructior
        self._board.set_position(*self._ui.board_position)

        # timing
        self._start_time = time.time()
        self._period = 1.0 / self._settings.REFRESH_RATE

        # load default terminal colors
        curses.use_default_colors()

        # init custom colors
        for idx, rgb in self._settings.CUSTOM_COLORS.items():
            curses.init_color(idx, *rgb)

        # init color pairs
        for idx, rgb in self._settings.COLOR_PAIRS.items():
            curses.init_pair(idx, *rgb)

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

    def switch_to_state(self, state: Type[GameState]) -> None:
        """Switches the game to the given state"""

        state_mapping = {
            Active: self._active,
            Ended: self._ended
        }

        self._state = state_mapping[state]

    def _wait_till_next_tick(self) -> None:
        """
        Ensures that 1s/refresh rate passes between every event loop iteration
        """
        time.sleep(self._period - ((time.time() - self._start_time) % self._period))

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

                    self._wait_till_next_tick()
                except KeyboardInterrupt:
                    # ignore
                    continue
        finally:
            # on sys.exit
            curses.endwin()
            print(':D')
