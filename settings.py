# TODO use json
class Settings:
    """
    Class containing game settings
    """
    def __init__(self):
        self._REFRESH_RATE = 30  # hz
        self._BOARD_SIZE = (10, 20)  # x, y
        self._WINDOW_SIZE = (72, 24)  # x, y
        self._BLOCK_MOVEMENT_PERIOD = 0.2  # s
        # TODO colors

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
