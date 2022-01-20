from abc import ABC, abstractmethod


class Subject(ABC):
    _observers = []

    @abstractmethod
    def attach_observer(self, obs) -> None:
        pass

    @abstractmethod
    def detach_observer(self, obs) -> None:
        pass

    @abstractmethod
    def notify(self):
        pass


class Observer(ABC):
    def update(self, game):
        pass


class ScoreObserver(Observer):
    def update(self, game):
        game.ui.lines = game.lines
        game.ui.level = game.level
        game.ui.score = game.score


class CountdownObserver(Observer):
    def update(self, game):
        if game.countdown.ticks_to_start == 1:
            num = 'GO!'
        else:
            num = game.countdown.ticks_to_start - 1
        game.ui.countdown = f"Get ready!\n\n{num}"


class StartingLevelObserver(Observer):
    def update(self, game):
        game.starting_level = game.start_level


class NextBlockObserver(Observer):
    def update(self, game):
        pass


class GameEndedObserver(Observer):
    def update(self, game):
        pass
