# class Board holds the chess board and its state
from abstractPiece import AbstractPiece
from concretePieces import Pawn, Rook, Horse, Bishop, Queen, King, PlaceHolder
from utils import InternalErrorException, Position, PieceColor, PieceType, Move, InvalidMoveException
import logging
import copy

logger = logging.getLogger()


class Board:
    _rubrics = None
    _pieces = None  # dict that holds all active pieces, split by color. piece_name->piece
    _removed_pieces = None  # dict that holds all captured pieces, split by color. piece_name->piece
    _current_side_color = None
    _other_side_color = None

    def __init__(self):
        self._rubrics = [[PlaceHolder(Position(y, x)) for x in range(8)] for y in range(8)]
        self._pieces = {PieceColor.WHITE: {}, PieceColor.BLACK: {}}
        self._removed_pieces = {PieceColor.WHITE: {}, PieceColor.BLACK: {}}
        self._current_side_color = PieceColor.WHITE
        self._other_side_color = PieceColor.BLACK

    @property
    def current_player_color(self):
        return self._current_side_color

    def get_board_copy(self):
        """returns a copy of this board"""
        board_copy = Board()
        board_copy._rubrics = copy.deepcopy(self._rubrics)
        board_copy._pieces = copy.deepcopy(self._pieces)
        board_copy._current_side_color = self._current_side_color
        board_copy._other_side_color = self._other_side_color
        return board_copy

    def switch_turns(self):
        self._current_side_color = PieceColor.BLACK if self._current_side_color == PieceColor.WHITE \
            else PieceColor.WHITE
        self._other_side_color = PieceColor.BLACK if self._current_side_color == PieceColor.WHITE else PieceColor.WHITE

    def rubric(self, position: Position):
        """a handy shortcut to get the contents of a specific rubric"""
        return self._rubrics[position.x][position.y]

    def set_rubric(self, piece: AbstractPiece, position: Position):
        """sets the given piece to the given position"""
        self._rubrics[position.x][position.y] = piece
        piece.position = position

    def get_attackers(self, attackers_color: PieceColor, attacked_position:Position):
        """return the list of pieces that are attacking the given position"""

        # scan all opposing pawns and horses on the board to see if any of them
        # is attacking the given position. Note: there may be multiple attackers
        # as allowed by the excercise, I'm not scanning for Checks by other pieces
        potential_attackers = ['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'HL', 'HR']
        attackers = []
        for attacker_name in potential_attackers:
            attacker = self._pieces[attackers_color].get(attacker_name, None)
            if attacker and attacker.is_attacking(attacked_position):  # some pieces may be gone by now
                attackers.append(attacker)

        return attackers

    def get_king_attackers(self):
        """returns a list of attackers to the current side's king"""
        # if the list is non-empty, we're in Check!
        other_side_color = PieceColor.BLACK if self._current_side_color == PieceColor.WHITE else PieceColor.WHITE
        king_position = self._pieces[self._current_side_color]['K'].position  # 'K' is for King!

        return self.get_attackers(other_side_color, king_position)

    def remove_piece(self, piece):
        """removes the given piece from the board and sets a placeholder instead"""
        if piece.color not in (PieceColor.BLACK, PieceColor.WHITE):
            raise InternalErrorException("cant remove a piece with no color")
        x, y = piece.position.x, piece.position.y
        # set placeholder in its place
        self._rubrics[x][y] = PlaceHolder(piece.position)

        # keep track of which pieces were removed
        if piece.name in self._removed_pieces[piece.color]:
            raise InternalErrorException("cant remove piece %s - already removed" % piece.name)
        self._removed_pieces[piece.color][piece.name] = piece
        self._pieces[piece.color].pop(piece.name)

    def move_piece(self, move: Move, ignore_check=False):
        """Moves a piece located in the given start_position to the given end_position"""
        # no need to check the values of Position as they are guaranteed to be sane.

        # sanity: cant move from a position onto itself
        if move.from_pos.to_str == move.to_pos.to_str:  # TODO compare by value, not str
            raise InvalidMoveException('cant move a piece onto itself (%s)' % move.from_pos.to_str())

        piece = self.rubric(move.from_pos)
        if piece is None:
            raise Exception("assert failed: found empty rubric at: %s" % move.from_pos.to_str())

        # sanity: there must be a piece in the start position:
        if piece.piece_type == PieceType.PLACEHOLDER:
            raise InvalidMoveException('cant move from empty rubric (%s)' % (move.from_pos.to_str()))

        # sanity: ensure the move is valid for this turn's color
        if piece.color != self._current_side_color:
            raise InvalidMoveException("cant move a piece of this color at this turn")

        # sanity: if capturing, pieces must have different colors
        captured_piece = self.rubric(move.to_pos)
        if captured_piece.piece_type != PieceType.PLACEHOLDER:
            if captured_piece.color == piece.color:
                raise InvalidMoveException('cant capture a piece of the same color (start: %s, end: %s)' %
                                           (move.from_pos.to_str(), move.to_pos.to_str()))

        # handle movement in Check
        king_attackers = self.get_king_attackers()
        if not ignore_check and len(king_attackers) > 0:
            # if the king is under attack (== Check), the only valid moves are those that
            # resolve the situation:
            # a) moving the king to an unattacked position
            # b) capturing the attacker by the king, provided its position is NOT attacked by another piece
            # c) capturing the attacker by another piece
            # d) blocking the check by a rook, queen or bishop: placing them between
            #   the king and the attacker - NOTE I will not implement this

            # if there are no valid moves, the game is over (Checkmate) - this is handled elsewhere

            # determine if the move will resolve the Check:
            # create a copy of the board, run the proposed move (ignore the check)
            # and then determine if we're still in check afterwards
            board_copy = self.get_board_copy()
            board_copy.move_piece(move, ignore_check=True)
            if len(board_copy.get_attackers(self._other_side_color, move.to_pos)) > 0:
                # the move did not resolve the check, so it wasnt valid:
                raise InvalidMoveException("move failed to resolve Check")

        if piece.is_valid_move(move, self._rubrics):
            # handle capture scenario
            if captured_piece.piece_type != PieceType.PLACEHOLDER:
                # remove the captured piece
                self.remove_piece(captured_piece)

            # move the piece to its destination
            self.set_rubric(piece, move.to_pos)

            # set empty placeholder in the origin rubric
            self.set_rubric(PlaceHolder(Position), move.from_pos)

        return True

    def detect_checkmate(self):
        """This function returns true if the current side is in Checkmate"""
        # checkmate detection is done as follows:
        # first we establish a list of the king possible moves (ignoring Check limitations)
        # then we play each of these moves and determine if we're still in check. if all moves
        # fail, we're in checkmate.

        # note: this approach is deliberately simplistic and does not take into account
        # resolving checkmate by other pieces.

        king = self._pieces[self._current_side_color]['K']  # should always be there. the king is never removed.
        king_next_positions = king.list_next_potential_positions(self._rubrics)
        if len(king_next_positions) == 0:
            # not likely but possible. the king must be physically surrounded by its own side's pieces and cant escape.
            return True

        # lets just try each and every possible move by the king:
        for next_position in king_next_positions:
            board_copy = self.get_board_copy()
            board_copy.move_piece(Move(king.position, next_position), ignore_check=True)
            if len(board_copy.get_king_attackers()) == 0:
                # moved out of check. yay
                return False
        return True

    def reset_pieces(self):
        """Inits the board: places the pieces in their initial positions"""
        color = PieceColor.WHITE
        white_pieces = self._pieces[PieceColor.WHITE]
        for i in range(8):
            name = 'P%s' % i
            piece = Pawn(color, Position(i, 1), name)
            white_pieces[name] = piece
            self._rubrics[i][1] = piece

        rook_left = Rook(color, Position(0, 0), 'RL')
        white_pieces[rook_left.name] = rook_left
        self._rubrics[0][0] = rook_left

        rook_right = Rook(color, Position(7, 0), 'RR')
        white_pieces[rook_right.name] = rook_right
        self._rubrics[7][0] = rook_right

        horse_left = Horse(color, Position(1, 0), 'HL')
        white_pieces[horse_left.name] = horse_left
        self._rubrics[1][0] = horse_left

        horse_right = Horse(color, Position(6, 0), 'HR')
        white_pieces[horse_right.name] = horse_right
        self._rubrics[6][0] = horse_right

        bishop_left = Bishop(color, Position(2, 0), 'BL')
        white_pieces[bishop_left.name] = bishop_left
        self._rubrics[2][0] = bishop_left

        bishop_right = Bishop(color, Position(5, 0), 'BR')
        white_pieces[bishop_right.name] = bishop_right
        self._rubrics[5][0] = bishop_right

        queen = Queen(color, Position(3, 0), 'Q')
        white_pieces[queen.name] = queen
        self._rubrics[3][0] = queen

        king = King(color, Position(4, 0), 'K')
        white_pieces[king.name] = king
        self._rubrics[4][0] = king

        color = PieceColor.BLACK
        black_pieces = self._pieces[PieceColor.BLACK]
        for i in range(8):
            piece = Pawn(color, Position(i, 6), 'P%s' % i)
            black_pieces[piece.name] = piece
            self._rubrics[i][6] = piece

        rook_left = Rook(color, Position(0, 7), 'RL')
        black_pieces[rook_left.name] = rook_left
        self._rubrics[0][7] = rook_left

        rook_right = Rook(color, Position(7, 7), 'KR')
        black_pieces[rook_right.name] = rook_right
        self._rubrics[7][7] = rook_right

        horse_left = Horse(color, Position(1, 7), 'HL')
        black_pieces[horse_left.name] = horse_left
        self._rubrics[1][7] = horse_left

        horse_right = Horse(color, Position(6, 7), 'HR')
        black_pieces[horse_right.name] = horse_right
        self._rubrics[6][7] = horse_right

        bishop_left = Bishop(color, Position(2, 7), 'BL')
        black_pieces[bishop_left.name] = bishop_left
        self._rubrics[2][7] = bishop_left

        bishop_right = Bishop(color, Position(5, 7), 'BR')
        black_pieces[bishop_right.name] = bishop_right
        self._rubrics[5][7] = bishop_right

        queen = Queen(color, Position(3, 7), 'Q')
        black_pieces[queen.name] = queen
        self._rubrics[3][7] = queen

        king = King(color, Position(4, 7), 'K')
        black_pieces[king.name] = king
        self._rubrics[4][7] = king

    def print(self):
        """Prints a crude representation of the game board"""
        print('   0    1    2    3    4    5    6    7')
        for j in range(7, -1, -1):
            row = '%s:' % j
            for i in range(8):
                row += self._rubrics[i][j].to_str_with_color
            print(row)
        print('   0    1    2    3    4    5    6    7')

        for key in self._removed_pieces[PieceColor.BLACK].keys():
            print('removed black piece: %s -> %s %s %s' % (
            key, self._removed_pieces[PieceColor.BLACK][key].position.to_str(),
            self._removed_pieces[PieceColor.BLACK][key].piece_type,
            self._removed_pieces[PieceColor.BLACK][key].name)
                  )

        for key in self._removed_pieces[PieceColor.WHITE].keys():
            print('removed white piece: %s -> %s %s %s' % (
            key, self._removed_pieces[PieceColor.WHITE][key].position.to_str(),
            self._removed_pieces[PieceColor.WHITE][key].piece_type,
            self._removed_pieces[PieceColor.WHITE][key].name)
                  )

        # for key in self._pieces[PieceColor.BLACK].keys():
        # print('black piece: %s -> %s %s %s' % (key, self._pieces[PieceColor.BLACK][key].position.to_str(),
        #                                       self._pieces[PieceColor.BLACK][key].piece_type,
        #                                       self._pieces[PieceColor.BLACK][key].name)
        #      )

        # for key in self._pieces[PieceColor.WHITE].keys():
        # print('white piece: %s -> %s %s %s' % (key, self._pieces[PieceColor.WHITE][key].position.to_str(),
        #                                       self._pieces[PieceColor.WHITE][key].piece_type,
        #                                       self._pieces[PieceColor.WHITE][key].name)
        #      )
