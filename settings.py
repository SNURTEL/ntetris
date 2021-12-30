# TODO use json
import curses


class Settings:
    """
    Class containing game settings
    """

    def __init__(self):
        self._REFRESH_RATE = 30  # hz
        self._BOARD_SIZE = (10, 20)  # x, y
        self._WINDOW_SIZE = (72, 24)  # x, y
        self._BLOCK_MOVEMENT_PERIOD = 0.2  # s

        self._CUSTOM_COLORS = {250: (1000, 500, 0),  # orange
                               251: (250, 250, 250)}  # background

        self._COLOR_PAIRS = {1: (curses.COLOR_WHITE, -1),  # text and UI
                             10: (251, -1),  # background
                             11: (-1, curses.COLOR_CYAN),  # blocks
                             12: (-1, curses.COLOR_BLUE),
                             13: (-1, 250),
                             14: (-1, curses.COLOR_YELLOW),
                             15: (-1, curses.COLOR_GREEN),
                             16: (-1, curses.COLOR_MAGENTA),
                             17: (-1, curses.COLOR_RED)}

    @property
    def CUSTOM_COLORS(self):
        return self._CUSTOM_COLORS

    @property
    def COLOR_PAIRS(self):
        return self._COLOR_PAIRS

    @property
    def REFRESH_RATE(self):
        return self._REFRESH_RATE

    @property
    def BOARD_SIZE(self):
        return self._BOARD_SIZE

    @property
    def WINDOW_SIZE(self):
        return self._WINDOW_SIZE

    @property
    def BLOCK_MOVEMENT_PERIOD(self):
        return self._BLOCK_MOVEMENT_PERIOD
