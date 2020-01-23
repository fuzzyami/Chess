from abc import ABC

from abstractPiece import AbstractPiece
import logging
from utils import Position, Move, PieceColor, PieceType, InvalidMoveException

logger = logging.getLogger()


class PlaceHolder(AbstractPiece):
    """represents a placeholder, a no-piece"""

    def __init__(self, position: Position):
        AbstractPiece.__init__(self, PieceType.PLACEHOLDER, PieceColor.NO_COLOR, position, "___")


class Pawn(AbstractPiece):
    """represents a Pawn"""

    def __init__(self, piece_color: PieceColor, position: Position, name: str):
        AbstractPiece.__init__(self, PieceType.PAWN, piece_color, position, name)
        _already_moved = False

    def is_valid_move(self, move: Move, rubrics):
        """given a move and the rubrics, returns True if the move is valid for this piece or throws exception"""
        # pawn can move one rubric forwards if not capturing.
        # note that 'forward' is color-specific: white grows on y-axis. black does the opposite
        # or one move diagonally forward if capturing
        # Note: it is also allowed to move twice on the first move, but I'm not doing that for now

        source_x, source_y = move.from_pos.x, move.from_pos.y
        dest_x, dest_y = move.to_pos.x, move.to_pos.y

        if self.color == PieceColor.WHITE and dest_y < source_y:
            raise InvalidMoveException("invalid move direction for white pawn")

        if self.color == PieceColor.BLACK and dest_y > source_y:
            raise InvalidMoveException("invalid move direction for black pawn")

        if abs(dest_y - source_y) != 1:
            raise InvalidMoveException("invalid move for pawn: can only jump one piece forwards")

        # are we moving one rubric forwards or diagonally?
        if source_x == dest_x:
            # moving straight - not capturing
            if rubrics[dest_x][dest_y].piece_type == PieceType.PLACEHOLDER:
                return True
        elif abs(dest_x - dest_y) == 1:
            # moving diagonally - capturing
            if rubrics[dest_x][dest_y].piece_type != PieceType.PLACEHOLDER:
                return True
        raise InvalidMoveException("invalid move for pawn")

    def is_attacking(self, attacked_position: Position):
        """returns True if this pawn is attacking the given position"""
        # pawn's attack direction depends on its color:
        if self.color == PieceColor.WHITE:
            if abs(self.position.x - attacked_position.x) == 1 and self.position.y + 1 == attacked_position.y:
                return True

        if self.color == PieceColor.BLACK:
            if abs(self.position.x - attacked_position.x) == 1 and self.position.y - 1 == attacked_position.y:
                return True
        return False

    def list_next_potential_positions(self, rubrics):
        """returns a list of potential and valid next positions for this piece, ignoring Check-semantics"""
        # TODO this code needs to be DRYied up.
        valid_positions = []
        if self.color == PieceColor.WHITE:
            # pawn cant move if already at the top:
            if self.position.y == 7:
                return valid_positions
            # there are 3 possible moves for white pawns: up, up-right or up-left.

            # you can only move up if its vacant
            up = Position(self.x, self.y + 1)
            if rubrics[up.x, up.y].piece_type == PieceType.PLACEHOLDER:
                valid_positions.append(up)

            # pawn can only capture right if not at right-most column
            # and only if there's a piece there and its of the opposite color.
            if self.x < 7:
                up_right = Position(self.x + 1, self.y + 1)
                capture_piece = rubrics[up_right.x, up_right.y]
                if capture_piece.piece_type != PieceType.PLACEHOLDER and capture_piece.color != self.color:
                    valid_positions.append(up_right)
            if self.x > 0:  # and similarly for the left-most column
                up_left = Position(self.x - 1, self.y + 1)
                capture_piece = rubrics[up_left.x, up_left.y]
                if capture_piece.piece_type != PieceType.PLACEHOLDER and capture_piece.color != self.color:
                    valid_positions.append(up_left)

        else:  # BLACK PAWN
            # pawn cant move if already at the bottom:
            if self.position.y == 0:
                return valid_positions
            # there are 3 possible moves for black pawns: down (walk) or capture: down-right or down-left.

            # you can only move down if its vacant
            down = Position(self.x, self.y - 1)
            if rubrics[down.x, down.y].piece_type == PieceType.PLACEHOLDER:
                valid_positions.append(down)

            # pawn can only capture right if not at right-most column
            # and only if there's a piece there and its of the opposite color.
            if self.x < 7:
                down_right = Position(self.x + 1, self.y - 1)
                capture_piece = rubrics[down_right.x, down_right.y]
                if capture_piece.piece_type != PieceType.PLACEHOLDER and capture_piece.color != self.color:
                    valid_positions.append(down_right)
            if self.x > 0:  # and similarly for the left-most column
                down_left = Position(self.x - 1, self.y - 1)
                capture_piece = rubrics[down_left.x, down_left.y]
                if capture_piece.piece_type != PieceType.PLACEHOLDER and capture_piece.color != self.color:
                    valid_positions.append(down_left)

        return valid_positions


class Bishop(AbstractPiece):
    """"represents a Bishop"""

    def __init__(self, piece_color: PieceColor, position: Position, name: str):
        AbstractPiece.__init__(self, PieceType.BISHOP, piece_color, position, name)

    def is_valid_move(self, move: Move, rubrics):
        """given a move and the rubrics, returns True if the move is valid for this piece or throws exception"""
        # bishop can move in one of the four diagonals
        # it cant jump over other pieces.

        source_x, source_y = move.from_pos.x, move.from_pos.y
        dest_x, dest_y = move.to_pos.x, move.to_pos.y

        if abs(dest_x - source_x) != abs(dest_y - source_y):
            raise InvalidMoveException("bishop can only move diagonally")

        # calculate the actual path taken to ensure we're not jumping over other pieces, which is illegal
        path = []

        distance = abs(dest_x - source_x + 1)
        if dest_x > source_x:  # moving right
            if dest_y > source_y:  # moving up
                for i in range(1, distance):
                    path.append(Position(source_x + i, source_y + i))
            else:  # moving down
                for i in range(1, distance):
                    path.append(Position(source_x + i, source_y - i))
        else:  # moving left
            if dest_y > source_y:  # moving up
                for i in range(1, distance):
                    path.append(Position(source_x - i, source_y + i))
            else:  # moving down
                for i in range(1, distance):
                    path.append(Position(source_x - i, source_y - i))

        # ensure there's nothing in our path:
        for rubric in path:
            if rubrics[rubric.x][rubric.y].piece_type != PieceType.PLACEHOLDER:
                raise InvalidMoveException("cant jump over piece in position %s,%s" % (rubric.x, rubric.y))

        return True

    def is_attacking(self, attacked_position: Position):
        """returns True if this piece is attacking the given position"""
        raise NotImplementedError("is_attacking is not implemented for Bishop")

    def list_next_potential_positions(self):
        """returns a list of potential and valid next positions for this piece, ignoring Check-semantics"""
        raise NotImplementedError("is_attacking is not implemented for Bishop")


class Rook(AbstractPiece):
    """"represents a Rook"""

    def __init__(self, piece_color: PieceColor, position: Position, name: str):
        AbstractPiece.__init__(self, PieceType.ROOK, piece_color, position, name)

    def is_valid_move(self, move: Move, rubrics):
        """given a move and the rubrics, returns True if the move is valid for this piece or throws exception"""
        # rook can move in straight lines: either up, down, left or right.
        # it cant jump over other pieces.

        source_x, source_y = move.from_pos.x, move.from_pos.y
        dest_x, dest_y = move.to_pos.x, move.to_pos.y

        if source_x != dest_x and source_y != dest_y:
            raise InvalidMoveException("rook cant move on both axes at once")

        # calculate the actual path taken to ensure we're not jumping over other pieces, which is illegal
        path = []
        if dest_x > source_x:  # move right
            for i in range(source_x + 1, dest_x, 1):
                path.append(Position(i, source_y))
        elif dest_x < source_x:  # move left
            for i in range(source_x - 1, dest_x, -1):
                path.append(Position(i, source_y))
        elif dest_y > source_y:  # move up
            for i in range(source_y + 1, dest_y, 1):
                path.append(Position(dest_x, i))
        else:  # move down
            for i in range(source_y - 1, dest_y, -1):
                path.append(Position(dest_x, i))

        # ensure there's nothing in our path:
        for rubric in path:
            if rubrics[rubric.x][rubric.y].piece_type != PieceType.PLACEHOLDER:
                raise InvalidMoveException("cant jump over piece in position %s,%s" % (rubric.x, rubric.y))
        return True

    def is_attacking(self, attacked_position: Position):
        """returns True if this piece is attacking the given position"""
        raise NotImplementedError("is_attacking is not implemented for Rook")

    def list_next_potential_positions(self):
        """returns a list of potential and valid next positions for this piece, ignoring Check-semantics"""
        raise NotImplementedError("is_attacking is not implemented for Rook")


class Horse(AbstractPiece):
    """"represents a Horse(knight)"""

    def __init__(self, piece_color: PieceColor, position: Position, name: str):
        AbstractPiece.__init__(self, PieceType.HORSE, piece_color, position, name)

    def is_valid_move(self, move: Move, rubrics):
        """given a move and the rubrics, returns True if the move is valid for this piece or throws exception"""
        # the horse can move like the letter L.
        # it can jump over other pieces so there's no need to ensure the path to the destination is clear.

        source_x, source_y = move.from_pos.x, move.from_pos.y
        dest_x, dest_y = move.to_pos.x, move.to_pos.y

        dx, dy = abs(dest_x - source_x), abs(dest_y - source_y)
        if not (dx ** 2 + dy ** 2 == 5):
            raise InvalidMoveException("the horse cant move like that")
        return True

    def is_attacking(self, attacked_position: Position):
        """returns True if this horse is attacking the given position"""
        dx, dy = abs(self.position.x - attacked_position.x), abs(self.position.y - attacked_position.y)
        return True if dx ** 2 + dy ** 2 == 5 else False

    def list_next_potential_positions(self, rubrics):
        """returns a list of potential and valid next positions for this piece, ignoring Check-semantics"""
        valid_positions = []
        coordinates = [(self.x + 1, self.y + 2),
                       (self.x - 1, self.y + 2),
                       (self.x + 1, self.y - 2),
                       (self.x - 1, self.y - 2),
                       (self.x + 2, self.y + 1),
                       (self.x - 2, self.y + 1),
                       (self.x + 2, self.y - 1),
                       (self.x - 2, self.y - 1)]

        positions_on_board = []
        # filter out off-board positions (for horses on the edge of the board)
        for coordinate in coordinates:
            try:
                positions_on_board.append(Position(coordinate[0], coordinate[1]))
            except Position.InvalidPositionError:
                pass
        # filter in vacant positions and positions belonging to the other side
        for position in positions_on_board:
            target_piece = rubrics[position.x][position.y]
            if target_piece.piece_type == PieceType.PLACEHOLDER:
                valid_positions.append(target_piece)
            elif target_piece.color != self.color:
                valid_positions.append(target_piece)

        return valid_positions


class Queen(AbstractPiece):
    """"represents a Queen"""

    def __init__(self, piece_color: PieceColor, position: Position, name: str):
        AbstractPiece.__init__(self, PieceType.QUEEN, piece_color, position, name)

    def is_valid_move(self, move: Move, rubrics):
        """given a move and the rubrics, returns True if the move is valid for this piece or throws exception"""
        # the queen moves like a rook OR a bishop.
        # it cant jump over other pieces

        # validate using a rook
        print('queen: %s ' % self.position.to_str())
        temp_rook = Rook(self.color, self.position, 'tmp')
        try:
            temp_rook.is_valid_move(move, rubrics)
        except InvalidMoveException:
            print('validating queen: not a valid rook-like move')
            pass
        else:
            return True

        # validate using a bishop
        temp_bishop = Bishop(self.color, self.position, 'tmp')
        try:
            temp_bishop.is_valid_move(move, rubrics)
        except InvalidMoveException:
            print('validating queen: not a valid bishop-like move')
            pass
        else:
            return True
        # not a rook or a bishop? invalid
        raise InvalidMoveException("not a valid move for a queen")

    def is_attacking(self, attacked_position: Position):
        """returns True if this piece is attacking the given position"""
        raise NotImplementedError("is_attacking is not implemented for Queen")

    def list_next_potential_positions(self):
        """returns a list of potential and valid next positions for this piece, ignoring Check-semantics"""
        raise NotImplementedError("is_attacking is not implemented for Queen")


class King(AbstractPiece):
    """"represents a King"""

    def __init__(self, piece_color: PieceColor, position: Position, name: str):
        AbstractPiece.__init__(self, PieceType.KING, piece_color, position, name)

    def is_valid_move(self, move: Move, rubrics):
        """given a move and the rubrics, returns True if the move is valid for this piece or throws exception"""
        # the king can move a single piece in any direction.
        # it cant jump over anything so there's no need to ensure the path to destination is clear

        source_x, source_y = move.from_pos.x, move.from_pos.y
        dest_x, dest_y = move.to_pos.x, move.to_pos.y

        if abs(source_x - dest_x) > 1 or abs(source_y - dest_y) > 1:
            raise InvalidMoveException("king cant move more than one rubric")

        return True

    def is_attacking(self, attacked_position: Position):
        """returns True if this piece is attacking the given position"""
        raise NotImplementedError("is_attacking is not implemented for King")

    def list_next_potential_positions(self, rubrics):
        """returns a list of potential and valid next positions for this piece, ignoring Check-semantics"""
        valid_positions = []
        x = self.position.x
        y = self.position.y

        coordinates = [(x + 1, y),
                       (x - 1, y),
                       (x, y - 1),
                       (x, y + 1),
                       (x + 1, y + 1),
                       (x - 1, y + 1),
                       (x + 1, y - 1),
                       (x - 1, y - 1)]

        positions_on_board = []
        # filter out off-board positions (for pieces on the edge of the board)
        for coordinate in coordinates:
            try:
                positions_on_board.append(Position(coordinate[0], coordinate[1]))
            except Position.InvalidPositionError:
                pass
        # filter in vacant positions and positions belonging to the other side
        for position in positions_on_board:
            target_piece = rubrics[position.x][position.y]
            if target_piece.piece_type == PieceType.PLACEHOLDER:
                valid_positions.append(target_piece.position)
            elif target_piece.color != self.color:
                valid_positions.append(target_piece.position)

        return valid_positions
