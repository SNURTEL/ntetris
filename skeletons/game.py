import curses
import time
from settings import Settings
from components import Board


class GameState:
    def __init__(self, game):
        self._game = game
        self._settings = Settings()

    @property
    def game(self):
        return self._game

    @property
    def settings(self):
        return self._settings

    def handle_events(self):
        pass


class Active(GameState):
    def __init__(self, game):
        super().__init__(game)

    def handle_events(self):
        pass  # call update method on every component


class Stopped(GameState):
    def __init__(self, game):
        super().__init__(game)

    def handle_events(self):
        pass  # call update method on every component


class Game:
    def __init__(self, screen):  # screen arg will be passed by the wrapper
        # managing states
        self._active = Active(self)
        self._stopped = Stopped(self)

        self._state = self._stopped

        # components
        self._settings = Settings()
        self._screen = screen
        self._board = Board(self)

        # timing
        self.start_time = time.time()
        self.period = 1.0 / self.settings.REFRESH_RATE

    @property
    def active(self):
        return self._active

    @property
    def stopped(self):
        return self._stopped

    @property
    def state(self):
        return self._state

    @property
    def settings(self):
        return self._settings

    @property
    def screen(self):
        return self._screen

    @state.setter
    def state(self, new: GameState):
        self._state = new

    def switch_to_state(self, state: GameState):
        self.state = state

    def handle_events(self):
        self.state.handle_events()

    def draw_components(self):
        # call draw method on every component
        pass

    def wait_till_next_tick(self):
        time.sleep(self.period - ((time.time() - self.start_time) % self.period))

    def run_game(self):
        self.switch_to_state(self.active)

        #  main event loop
        while True:
            self.handle_events()
            self.draw_components()

            self.wait_till_next_tick()
