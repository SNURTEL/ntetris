from __future__ import annotations

from abc import ABC, abstractmethod


class Observable:
    """
    Observable object, can be subscribed by observers
    """

    def __init__(self, observers: list = None):
        """
        Inits class Observable
        :param outer: Object in which the Observable is placed
        :param observers: Initial list of observers
        """
        if not observers:
            self._observers = []
        else:
            self._observers = observers

    def attach_observer(self, observer: Observer) -> None:
        """
        Attaches the observer to the observable
        :param observer: The observer to be attached
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer: Observer) -> None:
        """
        Detaches the observer from the observable
        :param observer: The observer to be detached
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, **kwargs):
        """
        If _changed flag is set, notifies all attached observers
        :param kwargs: additional kwargs passed to the observers
        """
        for observer in self._observers:
            observer.update(self, **kwargs)


class Observer(ABC):
    """
    Abstract base class for observers
    """

    @abstractmethod
    def update(self, observable: Observable, **kwargs) -> None:
        """
        Does something after being called by the Observable
        :param observable:
        :param kwargs:
        :return:
        """
        pass
