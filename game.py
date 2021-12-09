import curses
import time
from settings import Settings
from random import randint
from classes import Board


class Game:
    """"""

    def __init__(self, screen):
        """

        :param screen: a curses.window instance used for displaying the UI
        """
        self.settings = Settings()
        self.screen = screen  # TODO use private attributes
        self.active = False
        self.screen = screen
        self.board = Board(self)
        self.start_time = time.time()
        self.period = 1.0 / self.settings.REFRESH_RATE

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
        self.resize_window()
        # self.draw_test()
        self.draw_board()

    def check_events(self):
        """Checks for any events that could happen in the game"""
        pass

    def draw_test(self):

        self.screen.addch(randint(0, 19), randint(0, 9), 'X')
        time.sleep(0.1)


    def draw_board(self):
        self.board.draw()

    def resize_window(self):
        y, x = 20, 10
        curses.resizeterm(y, x)
        is_resized = curses.is_term_resized(y, x)
        if is_resized:
            print('resized')
