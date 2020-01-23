# the game file is the top-level entity of the chess game simulation.
# it holds the players and the board entities
from board import Board
from utils import Position, Move, PieceColor, call_timeout
import logging
from enum import Enum
from player import Player

logger = logging.getLogger()


def get_next_move(f):
    """Get the next move from the player"""
    # this is the spot where we need to handle potentially malicious code, so lets run this in
    # another thread and monitor how long it takes to get the next move
    try:
        return call_timeout(Game.MAX_SECONDS_TO_WAIT_FOR_PLAYER_INPUT, f)
    except Exception:
        raise Game.InvalidGameInputException("no valid input from player")


class Game:

    MAX_SECONDS_TO_WAIT_FOR_PLAYER_INPUT = 1

    class InvalidGameInputException(Exception):
        """for when the player's input is either bad or just takes too long"""
        pass

    _playerOne = None
    _playerTwo = None
    _board = None
    _game_state = None

    class State(Enum):
        ONGOING = 1
        BLACK_WON = 2
        WHITE_WON = 3

    def __init__(self, player1: Player, player2: Player):
        self._board = Board()
        logger.info('resetting pieces on the board')
        self._board.reset_pieces()
        self._game_state = Game.State.ONGOING
        self._playerOne = player1
        self._playerTwo = player2
        self._current_player = player1 # player 1 is WHITE

    @property
    def game_state(self):
        return self._game_state

    @property
    def current_player(self):
        return self._current_player

    def switch_players(self):
        self._current_player = self._playerTwo if self._current_player == self._playerOne else self._playerOne

    def run(self):
        while self.game_state == Game.State.ONGOING:
            # get the next move from the current player:
            move = get_next_move(self.current_player.next_move)
            # apply the move onto the board
            self._board.move_piece(move)
            self._board.print()

            # switch sides
            self._board.switch_turns()
            self.switch_players()

            # detect game over conditions for current color
            if self._board.detect_checkmate():
                if self._board.current_player_color == PieceColor.WHITE:
                    self._game_state == Game.State.BLACK_WON
                else:
                    self._game_state == Game.State.WHITE_WON


def start_game():
    print('starting game...')
    p1 = Player([Move(Position(1, 1), Position(1, 2))])
    p2 = Player([Move(Position(1, 6), Position(1, 5))])
    game = Game(p1, p2)
    game.run()


if __name__ == "__main__":
    start_game()
