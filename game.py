from __future__ import annotations
import curses
import time
from settings import Settings
from components import Board
from abc import ABC, abstractmethod
from ui import UI


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
        key = self.game.screen.getch()

        self.game.board.update(key)

    def update_screen(self) -> None:
        """
        Draws the board and the UI
        """

        self.game.screen.erase()

        self.game.ui.draw_board()
        self.game.ui.draw_score()
        self.game.ui.draw_next()

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

        # UI
        curses.curs_set(False)
        self.ui = UI(self)

        self._screen.idcok(False)  # use if flickering appears
        self._screen.idlok(False)

        # cannot be done in UI class constructior
        self.board.set_position(*self.ui.board_position)

        # timing
        self.start_time = time.time()
        self.period = 1.0 / self.settings.REFRESH_RATE

        # color_presets
        curses.use_default_colors()

        curses.init_pair(1, curses.COLOR_WHITE, -1)

        curses.init_pair(11, -1, curses.COLOR_CYAN)
        curses.init_pair(12, -1, curses.COLOR_BLUE)
        curses.init_color(250, 1000, 500, 0)  # does not work in pycharm terminal
        curses.init_pair(13, -1, 250)
        curses.init_pair(14, -1, curses.COLOR_YELLOW)
        curses.init_pair(15, -1, curses.COLOR_GREEN)
        curses.init_pair(16, -1, curses.COLOR_MAGENTA)
        curses.init_pair(17, -1, curses.COLOR_RED)

        curses.init_pair(7, 250, -1)

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

            self.ui.resize()

            self.wait_till_next_tick()
