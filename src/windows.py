from __future__ import annotations
from typing import *

import curses
from abc import ABC

import src.settings as settings
from src.drawables import Drawable, NText, NBox, NFrame, BoardDrawable
from src.board import Board


class Window(Drawable, ABC):
    def __init__(self, screen: curses.window):
        super(Window, self).__init__(screen, 0, 0)
        self._contents = []
        pass

    def draw(self) -> None:
        for drawable in self._contents:
            drawable.draw()


class GameActiveWindow(Window):
    def __init__(self, screen: curses.window, board: Board):
        super(GameActiveWindow, self).__init__(screen)
        board_x = 27
        board_y = 2
        self._board_frame = NFrame(screen,
                                   board_x - 1,
                                   board_y - 1,
                                   2 * settings.BOARD_SIZE[0] + 2,
                                   settings.BOARD_SIZE[1] + 2,
                                   title='Game')
        self._contents.append(self._board_frame)

        self._board_drawable = BoardDrawable(screen, board_x, board_y, board)
        self._contents.append(self._board_drawable)
