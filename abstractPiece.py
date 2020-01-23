
from utils import Position, PieceColor, PieceType, Move

class AbstractPiece:
    """represents an abstract chess piece, with properties common to all the concrete pieces"""

    _color = None
    _type = None
    _position = None
    _name = None  # a unique name for the piece, like 'RR' - rook right or 'HL' - white horse left

    def __init__(self, piece_type: PieceType, piece_color: PieceColor, position: Position, name: str):
        self._type = piece_type
        self._color = piece_color
        self._position = position
        self._name = name

    def is_valid_move(self, move: Move, rubrics):
        """throws an InvalidMoveException if the given move is somehow illegal for this piece and given board"""
        raise NotImplementedError("is_valid_move is not implemented for AbstractPiece")

    def is_attacking(self, attacked_position: Position):
        """returns True if this piece is attacking the given position"""
        raise NotImplementedError("is_attacking is not implemented for AbstractPiece")

    def list_next_potential_positions(self):
        """returns a list of potential and valid next positions for this piece, ignoring Check-semantics"""
        raise NotImplementedError("is_attacking is not implemented for AbstractPiece")

    @property
    def color(self):
        return self._color

    @property
    def piece_type(self):
        return self._type

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = val

    @property
    def name(self):
        return self._name

    @property
    def to_str(self):
        return '|%s|' % self._name if len(self._name) == 3 else '|_%s|' % self._name

    @property
    def to_str_with_color(self):
        """return a string representation of the piece, like BHR or WP1"""
        # add color prefix to all the pieces that are not placeholders
        color_prefix = ''
        if self.piece_type != PieceType.PLACEHOLDER:
            color_prefix = 'W' if self.color == PieceColor.WHITE else 'B'
        name = '%s%s' % (color_prefix, self._name)
        return '|%s|' % name if len(name) == 3 else '|_%s|' % name

