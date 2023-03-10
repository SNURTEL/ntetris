from __future__ import annotations
from typing import *

from abc import ABC, abstractmethod

import curses

from src.board import Board


class Drawable(ABC):
    def __init__(self, screen, x: int, y: int):
        self.x = x
        self.y = y
        self._screen = screen

    @abstractmethod
    def draw(self) -> None:
        pass


class NText(Drawable):
    def __init__(self, screen, text: str, x: int, y: int, color: int, *, alignment='left', blinking=False):
        super(NText, self).__init__(screen, x, y)
        self.color = color
        self.alignment = alignment
        self.blinking = blinking

        self.lines = self.align_lines(text)

    def align_lines(self, text: str) -> List[str]:
        width = max([len(line) for line in text.split('\n')])
        align = str.rjust if self.alignment == 'right' \
            else str.center if self.alignment == 'center' \
            else str.ljust
        return [align(line, width) for line in text.split('\n')]

    def draw(self) -> None:
        for idx, line in enumerate(self.lines):
            self._screen.addstr(self.y + idx,
                                self.x,
                                line,
                                self.color | (curses.A_BLINK if self.blinking else 1))


class Rect(Drawable, ABC):
    def __init__(self, screen, x: int, y: int, size_x: int, size_y: int):
        super(Rect, self).__init__(screen, x, y)
        self.size_x = size_x
        self.size_y = size_y

        self._subwin = self._screen.subwin(size_y, size_x, y, x)
        self._subwin.idcok(False)
        self._subwin.idlok(False)


class NBox(Rect):
    def __init__(self, screen, x: int, y: int, size_x: int, size_y: int):
        super(NBox, self).__init__(screen, x, y, size_x, size_y)
        self._subwin.bkgd(' ', curses.COLOR_WHITE | curses.A_BOLD)

    def draw(self) -> None:
        self._subwin.clear()


class NFrame(Rect):
    def __init__(self, screen, x: int, y: int, size_x: int, size_y: int, title=''):
        super(NFrame, self).__init__(screen, x, y, size_x, size_y)

        self._title = NText(screen, title, x + (size_x - len(title)) // 2, y, curses.color_pair(1))

    def draw(self) -> None:
        self._subwin.border(0)
        self._title.draw()


class BoardDrawable(Drawable):
    def __init__(self, screen, x, y, board: Board):
        super(BoardDrawable, self).__init__(screen, x, y)
        self._board = board

    def draw(self) -> None:
        for col_i in range(self._board.size_x):
            for row_i in range(self._board.size_y):
                field = self._board.contents[col_i][row_i]
                if field:
                    self._screen.addstr(self.y + row_i, self.x + 2 * col_i, '  ',
                                        field | curses.A_BOLD)
                else:
                    self._screen.addch(self.y + row_i, self.x + 2 * col_i +1, '.',
                                       curses.color_pair(10) | curses.A_BOLD)

        for tile_x, tile_y in self._board.newblock_tiles:
            self._screen.addstr(self.y + tile_y, self.x + 2 * tile_x, '  ',
                                curses.color_pair(self._board.newblock_color) | curses.A_BOLD)
