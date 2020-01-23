from utils import Move
from time import sleep

class Player:
    """represents a player, an entity that provides moves for the chess game"""
    class NoMoreMovesException(Exception):
        pass
    _moves_list = None

    def __init__(self, moves_list: list):
        """init a player, with a pre-set list of moves"""
        self._moves_list = moves_list

    def next_move(self):
        """get the next move for this player"""
        if len(self._moves_list) == 0:
            raise Player.NoMoreMovesException("no more moves for player")
        sleep(0.5)
        return self._moves_list.pop(0)

    def set_next_move(self, move: Move):
        """push the next move into the moves list"""
        self._moves_list.insert(0, move)
