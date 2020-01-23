from abc import abstractmethod, ABC
from enum import Enum
from threading import Thread


class InternalErrorException(Exception):
    pass


class InvalidMoveException(Exception):
    pass


class PieceType(Enum):
    """represents the piece's chess class. an empty rubric is modeled as a PLACEHOLDER piece"""
    PLACEHOLDER = -1  # represents an empty rubric
    PAWN = 0
    BISHOP = 1
    ROOK = 2
    HORSE = 3  # used "horse" in stead "knight" to simplify notation (H for horse)
    QUEEN = 4
    KING = 5


class PieceColor(Enum):
    """represents a piece color, but also the current turn"""
    NO_COLOR = -1  # PLACEHOLDER pieces have no color
    WHITE = 1
    BLACK = 2


class Position:
    """represents a position on the board"""

    class InvalidPositionError(Exception):
        pass

    _pos_x = None
    _pos_y = None

    def __init__(self, x: int, y: int):
        if (x < 0 or x > 7) or (y < 0 or y > 7):
            raise Position.InvalidPositionError("invalid position: x:%s y:%s" % (x, y))
        self._pos_x = x
        self._pos_y = y

    @property
    def x(self):
        return self._pos_x

    @property
    def y(self):
        return self._pos_y

    @x.setter
    def x(self, val):
        self._pos_x = val

    @y.setter
    def y(self, val):
        self._pos_y = val

    def to_str(self):
        return 'x:%s y:%s' % (self._pos_x, self._pos_y)


class Move:
    """represents a move, which is composed of start and end positions"""
    _from_pos = None
    _to_pos = None

    def __init__(self, from_pos: Position, to_pos: Position):
        self._from_pos = from_pos
        self._to_pos = to_pos

    @property
    def from_pos(self):
        return self._from_pos

    @property
    def to_pos(self):
        return self._to_pos


class ExternalFunctionTookTooLongException(Exception):
    pass

def call_timeout(timeout, func, args=(), kwargs={}):
    if type(timeout) not in [int, float] or timeout <= 0.0:
        print("Invalid timeout!")

    elif not callable(func):
        print("{} is not callable!".format(type(func)))

    else:
        t = ThreadWithReturnValue(target=func, args=args, kwargs=kwargs)
        t.start()
        retval = (t.join(timeout))

        if t.is_alive():
            raise ExternalFunctionTookTooLongException("function too too long to run")
        else:
            return retval


class ThreadWithReturnValue(Thread):
    """a thread that returns the called function's value on join()"""
    #  Shamelessly stolen and slightly modified from https://stackoverflow.com/a/40344234/1277048
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        Thread.__init__(self, group, target, name, args, kwargs, daemon=daemon)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, timeout):
        Thread.join(self, timeout=timeout)
        return self._return