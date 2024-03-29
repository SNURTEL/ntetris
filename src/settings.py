import curses

REFRESH_RATE = 60
BOARD_SIZE = (10, 20)
WINDOW_SIZE = (78, 24)
BLOCK_MOVEMENT_PERIODS = {0: 0.8,
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

CUSTOM_COLORS = {250: (1000, 500, 0),  # orange
                 251: (250, 250, 250)}  # background; unused

COLOR_PAIRS = {1: (curses.COLOR_WHITE, -1),  # text and UI
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
SCOREBOARD_FILENAME = 'scoreboard.json'
