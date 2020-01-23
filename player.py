from utils import Move, Position
from time import sleep


class Player:
    """represents a player, an entity that provides moves for the chess game"""

    class NoMoreMovesException(Exception):
        pass

    _moves_list = None
    _name = None

    def __init__(self, name: str, filename: str):
        """init a player, reading its list of moves from the given filename"""
        self._moves_list = self.read_moves(open(filename, "r")) # note no attempt was made to make this code safe
        self._name = name

    def read_moves(self, filecontents: str):
        moves = []
        for line in filecontents:
            coords = list(map(int, line.split(',')))
            moves.append(Move(Position(coords[0], coords[1]), Position(coords[2], coords[3])))
        return moves

    def next_move(self):
        """get the next move for this player"""
        if len(self._moves_list) == 0:
            raise Player.NoMoreMovesException("no more moves for player %s" % self._name)
        return self._moves_list.pop(0)

    def set_next_move(self, move: Move):
        """push the next move into the moves list"""
        self._moves_list.insert(0, move)
