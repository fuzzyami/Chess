# the game file is the top-level entity of the chess game simulation.
# it holds the players and the board entities
from board import Board
from utils import Position, Move, PieceColor, call_timeout
import logging
from enum import Enum
from player import Player
import argparse

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
        BORKED = 4

    def __init__(self, board_layout_filename: str, player1: Player, player2: Player):
        self._board = Board()
        logger.info('resetting pieces on the board')
        self._board.set_pieces(board_layout_filename)
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
        """runs the game until its conclusion or exception"""
        try:
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
                        self._game_state = Game.State.BLACK_WON
                    else:
                        self._game_state = Game.State.WHITE_WON
        except Exception as e:
            print(e)
            self._game_state = Game.State.BORKED

        return self._game_state


def start_game(board_layout_filename: str, player1_moves_filename: str, player2_moves_filename: str):
    print('starting game...')
    p1 = Player("Player1", player1_moves_filename)
    p2 = Player("Player2", player2_moves_filename)
    game = Game(board_layout_filename, p1, p2)

    print("game result: %s" % game.run())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='run the chess simulation')
    parser.add_argument('player1_moves_file', type=str)
    parser.add_argument('player2_moves_file', type=str)
    parser.add_argument('board_layout', type=str)
    args = parser.parse_args()
    start_game(args.board_layout, args.player1_moves_file, args.player2_moves_file)
