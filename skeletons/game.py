import curses
from settings import Settings


class GameState:
    def __init__(self, game):
        self._game = game
        self._settings = Settings()
        # board

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
        pass


class Stopped(GameState):
    def __init__(self, game):
        super().__init__(game)

    def handle_events(self):
        pass


class Game:
    def __init__(self, screen):  # screen arg will be passed by the wrapper
        # managing states
        self._active = Active(self)
        self._stopped = Stopped(self)

        self._state = self._stopped

        # components
        self._settings = Settings()
        self._screen = screen


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

    def run_game(self):
        self.switch_to_state(self.active)

        # event loop


