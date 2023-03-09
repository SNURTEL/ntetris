from __future__ import annotations
from typing import *

from abc import ABC, abstractmethod

import curses


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
        super(NText, self).__init__(x, y, screen)
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


class Square(Drawable):
    def __init__(self, screen, x: int, y: int, size_x: int, size_y: int):
        super(Square, self).__init__(screen, x, y)
        self.size_x = size_x
        self.size_y = size_y

        self._subwin = self._screen.subwin(size_y, size_x, y, x)
        self._subwin.idcok(False)
        self._subwin.idlok(False)


class NBox(Square):
    def __init__(self, screen, x: int, y: int, size_x: int, size_y: int):
        super(NBox, self).__init__(screen, x, y, size_x, size_y)
        self._subwin.bkgd(' ', curses.COLOR_WHITE | curses.A_BOLD)

    def draw(self) -> None:
        self._subwin.clear()


class NFrame(Square):
    def __init__(self, screen, x: int, y: int, size_x: int, size_y: int, title=''):
        super(NFrame, self).__init__(screen, x, y, size_x, size_y)

        self._title = NText(screen, title, x + (size_x - len(title)) // 2, y, curses.color_pair(1))

    def draw(self) -> None:
        self._subwin.border(0)
        self._title.draw()
