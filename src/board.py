from __future__ import annotations
from typing import *

import random

from src.observers import Observable


class Board(Observable):
    BLOCKS = (
        [(pos, 0) for pos in range(4)],  # cyan
        [(pos, 1) for pos in range(3)] + [(0, 0)],  # blue
        [(pos, 1) for pos in range(3)] + [(2, 0)],  # orange
        [(0, 0), (0, 1), (1, 0), (1, 1)],  # yellow
        [(1, 0), (2, 0), (0, 1), (1, 1)],  # green
        [(pos, 1) for pos in range(3)] + [(1, 0)],  # purple
        [(0, 0), (1, 0), (1, 1), (2, 1)]  # red
    )
    # c, b, o, y, g, p, r
    COLORS = list(range(10, 18))

    def __init__(self, size_x, size_y):
        super(Board, self).__init__()
        self.contents = [[None for _ in range(size_y)] for _ in range(size_x)]
        self.newblock_tiles, self.newblock_color = self._get_random_block()
        self.nextblock_tiles, self.nextblock_col = self._get_random_block()

    def move_block(self, dir: str) -> bool:  # n, s, w, e
        x_offset = -1 if dir is 'w' else 1 if dir is 'e' else 0
        y_offset = -1 if dir is 'n' else 1 if dir is 's' else 0
        new_position = [(x + x_offset, y + y_offset) for x, y in self.newblock_tiles]
        if not self._validate_position(new_position):
            return False
        self.newblock_tiles = new_position
        self.notify()
        return True

    def rotate_block(self, dir: str) -> bool:  # l, r
        # relative to block's upper left tile
        pivot_x = 1 + min(x for x, _ in self.newblock_tiles)
        pivot_y = 0 if self.newblock_color is not 'c' else 1 + min(x for x, _ in self.newblock_tiles)

        dir = 1 if dir == 'r' else -1
        rotated = [((pivot_y - y) * dir + pivot_x,
                    (-1 if self.newblock_color == 'c' else 1) * (-pivot_x + x) * dir + pivot_y)
                   for x, y in self.newblock_tiles]
        if not self._validate_position(rotated):
            return False

        self.newblock_tiles = rotated
        return True

    def _validate_position(self, new_position) -> bool:
        if any([x not in range(0, self.size_x) or
                y not in range(0, self.size_y)
                for x, y in new_position]):
            return False
        return any([self.contents[x][y] is not None
                    for x, y in new_position])

    def place_block(self) -> None:
        for x, y in self.newblock_tiles:
            self.contents[x][y] = self.newblock_color
        self.newblock_tiles, self.newblock_color = self._get_random_block()

        self.notify()

    def _get_random_block(self) -> Tuple[List, str]:
        pick = random.randint(0, 6)
        x_offset = random.randint(3, 5)
        return [(x + x_offset, y) for x, y in Board.BLOCKS[pick]], Board.COLORS[pick]

    @property
    def size_x(self) -> int:
        return len(self.contents)

    @property
    def size_y(self) -> int:
        return len(self.contents[0])
