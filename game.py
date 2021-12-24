from __future__ import annotations
import curses
import time
from settings import Settings
from components import Board
from abc import ABC, abstractmethod


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

    def resize_window(self) -> None:
        """
        Resizes the window to dimensions specified in game settings
        """
        x, y = self._game.window_size
        is_resized = curses.is_term_resized(y, x)
        if is_resized:
            curses.resizeterm(y, x)


class Active(GameState):
    """
    Active state of the game
    """

    #  what about __init__? Seems to work just fine without it...

    def handle_events(self) -> None:
        """
        Reads keyboard input, updates the board and the UI
        """
        key = self.game.screen.getch()

        self.game.board.update(key)

    def update_screen(self) -> None:
        """
        Draws the board and the UI
        """
        self.game.screen.clear()
        self.resize_window()
        self.game.board.draw()
        self.game.screen.refresh()


class Stopped(GameState):
    """
    Stopped state of the game
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
        print('game stopped')


class Game:
    """
    Main class representing a Tetris game. Settings are loaded from settings.py # TODO update if this changes
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
        self._stopped = Stopped(self)

        self._state = self._stopped

        # window
        self.window_size = self._settings.WINDOW_SIZE
        curses.curs_set(False)

        # timing
        self.start_time = time.time()
        self.period = 1.0 / self.settings.REFRESH_RATE

        # color_presets
        curses.init_pair(11, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(12, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_color(250, 1000, 500, 0)  # does not work in pycharm terminal
        curses.init_pair(13, 250, curses.COLOR_BLACK)
        curses.init_pair(14, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(15, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(16, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(17, curses.COLOR_RED, curses.COLOR_BLACK)

        curses.init_pair(7, 250, curses.COLOR_BLACK)

    @property
    def active(self) -> GameState:
        return self._active

    @property
    def stopped(self) -> GameState:
        return self._stopped

    @property
    def state(self) -> GameState:
        return self._state

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def screen(self) -> curses.window:
        return self._screen

    @property
    def board(self) -> Board:
        return self._board

    @state.setter
    def state(self, new: GameState):
        self._state = new

    def switch_to_state(self, state: GameState) -> None:
        """Switches the game to the given state"""
        self.state = state

    def wait_till_next_tick(self) -> None:
        """
        Ensures that 1s/refresh rate passes between every event loop iteration
        """
        time.sleep(self.period - ((time.time() - self.start_time) % self.period))

    def run_game(self) -> None:
        """
        Starts the game
        """
        self.switch_to_state(self.active)
        self.start_time = time.time()

        #  main event loop
        while True:
            self.state.handle_events()
            self.state.update_screen()

            self.wait_till_next_tick()
