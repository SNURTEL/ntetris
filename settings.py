import curses


class Settings:
    """
    Class containing game settings
    """

    def __init__(self):
        self._REFRESH_RATE = 60  # hz
        self._BOARD_SIZE = (10, 20)  # x, y
        self._WINDOW_SIZE = (78, 24)  # x, y
        self._BLOCK_MOVEMENT_PERIODS = {0: 0.8,
                                        1: 0.7166667,
                                        2: 0.6333333,
                                        3: 0.55,
                                        4: 0.4666667,
                                        5: 0.3833333,
                                        6: 0.3,
                                        7: 0.2166667,
                                        8: 0.1333333,
                                        9: 0.1,
                                        10: 0.083333,
                                        13: 0.066667,
                                        16: 0.05,
                                        19: 0.033333,
                                        29: 0.016667}  # level: t[s]

        self._CUSTOM_COLORS = {250: (1000, 500, 0),  # orange
                               251: (250, 250, 250)}  # background; unused

        self._COLOR_PAIRS = {1: (curses.COLOR_WHITE, -1),  # text and UI
                             2: (curses.COLOR_YELLOW, -1),  # colored text
                             10: (251, -1),  # background
                             11: (-1, curses.COLOR_CYAN),  # blocks
                             12: (-1, curses.COLOR_BLUE),
                             13: (-1, 250),
                             14: (-1, curses.COLOR_YELLOW),
                             15: (-1, curses.COLOR_GREEN),
                             16: (-1, curses.COLOR_MAGENTA),
                             17: (-1, curses.COLOR_RED),
                             20: (-1, -1)  # background (the actual one)
                             }
        self._SCOREBOARD_FILENAME = 'scoreboard.json'

    @property
    def SCOREBOARD_FILENAME(self):
        return self._SCOREBOARD_FILENAME

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
    def BLOCK_MOVEMENT_PERIODS(self):
        return self._BLOCK_MOVEMENT_PERIODS
