import curses
import time
from settings import Settings
from random import randint


class Game:
    """"""
    def __init__(self, screen):
        """

        :param screen: a curses.window instance used for displaying the UI
        """
        self.active = False
        self.settings = Settings()
        self.screen = screen
        self.start_time = time.time()
        self.period = 1.0 / self.settings.refresh_rate

    def run_game(self):
        """Runs the main loop"""
        self.active = True
        self.start_time = time.time()
        while True:
            self.check_events()
            self.update_screen()
            self.screen.refresh()

            # wait till next tick
            time.sleep(self.period - ((time.time() - self.start_time) % self.period))

    def update_screen(self):
        """Re-draws the UI"""
        self.draw_test()

    def check_events(self):
        """Checks for any events that could happen in the game"""
        pass

    def draw_test(self):
        self.screen.addstr(randint(0, 10), randint(0, 10), 'hemlo')
