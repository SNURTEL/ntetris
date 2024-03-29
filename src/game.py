from __future__ import annotations

from typing import *

import time
import curses
import threading

from pynput.keyboard import KeyCode, Listener, Key

import src.settings as settings
from src.board import Board
from src.stats import Stats
from src.windows import GameActiveWindow


def run_game(screen: curses.window):
    game = Game(screen)

    curses.use_default_colors()
    curses.curs_set(0)
    for idx, rgb in settings.CUSTOM_COLORS.items():
        curses.init_color(idx, *rgb)
    for idx, rgb in settings.COLOR_PAIRS.items():
        curses.init_pair(idx, *rgb)

    threads = [
        threading.Thread(target=_game_thread, args=(game,)),
        threading.Thread(target=_ui_thread, args=(game,), daemon=True),
        threading.Thread(target=_timer_thread, args=(game,), daemon=True)
    ]

    for thread in threads:
        thread.start()

    threads[0].join()
    curses.flushinp()


def _game_thread(game: Game):
    with Listener(
            on_press=game.handle_key_press,
            on_release=game.handle_key_release
    ) as listener:
        listener.join()


def _ui_thread(game: Game):
    refresh_delay = 1. / settings.REFRESH_RATE
    while True:
        time.sleep(refresh_delay)
        game.redraw_screen()


def _timer_thread(game: Game):
    game.handle_timer()
    threading.Timer(0.5, _timer_thread, (game,)).start()


class Game:
    def __init__(self, screen):
        self._screen = screen
        self._board = Board(*settings.BOARD_SIZE)
        self._stats = Stats()
        self._window = GameActiveWindow(screen, self._board, self._stats)

        self.ended = False

    def handle_key_press(self, key: KeyCode):
        with threading.Lock():
            if key == Key.left:
                self._board.move_block('w')
            elif key == Key.right:
                self._board.move_block('e')
            elif key == Key.up:
                self._board.rotate_block('r')
            elif key == Key.down:
                drop_pts = 0
                while self._board.move_block('s'):
                    drop_pts += 2
                    pass
                lines = self._board.place_block()
                Stats.score += Stats.level * (0, 40, 100, 300, 1200)[lines] + drop_pts
                Stats.lines += lines
                if Stats.lines >= 5 * (Stats.level + 1) * Stats.level:
                    Stats.level += 1

    def handle_timer(self):
        with threading.Lock():
            if self._board.move_block('s'):
                return

            Stats.score += Stats.level * (40, 100, 300, 1200)[self._board.place_block() - 1]

    def handle_key_release(self, key: Key):
        with threading.Lock():
            if key == Key.esc:
                self.ended = True
                return False

    def redraw_screen(self):
        self._screen.erase()
        self._window.draw()
        self._screen.refresh()
