import curses
from settings import Settings


class Board:
    def __init__(self):
        self.settings = Settings()
        self.size_x = self.settings.board_size[0]
        self.size_y = self.settings.board_size[1]
        self.board = [[None for i in range(self.size_y)] for j in range(self.size_x)]