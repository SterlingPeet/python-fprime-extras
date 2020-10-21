

from abc import ABCMeta, abstractmethod


class AbstractRule(metaclass=ABCMeta):
    """Base class for defining linter rules."""

    # def __init__(self):
    #     self.__fixable = False

    @property
    @abstractmethod
    def tags(self):
        pass

    @property
    @abstractmethod
    def fixable(self):
        pass

    # @fixable.setter
    # @abstractmethod
    # def fixable(self, fixable):
    #     self.__fixable = fixable

