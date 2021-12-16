import curses
from settings import Settings


# pre-written
class Board:
    def __init__(self, game):
        self.screen = game.screen
        self.settings = game.settings
        self.size_x = self.settings.BOARD_SIZE[0]
        self.size_y = self.settings.BOARD_SIZE[1]
        self.test_char = 'X'
        self.board = [[self.test_char for i in range(self.size_y)] for j in range(self.size_x)]

    def draw(self):
        for i in range(self.size_x):
            for j in range(self.size_y):
                try:
                    self.screen.addch(j, i, self.board[i][j])  # FIXME RETURNED ERR DZIEKI MORDO
                except curses.error:
                    pass
