from __future__ import annotations
from typing import *


class Stats:
    score = 0
    lines = 0
    level = 1

    @classmethod
    def reset(cls):
        cls.score = 0
        cls.lines = 0
        cls.level = 1
