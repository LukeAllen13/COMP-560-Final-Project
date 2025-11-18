# engine/piece_types.py
from dataclasses import dataclass
from typing import List, Tuple

WHITE = 1
BLACK = -1
PAWN_VALUE = 1

Vector = Tuple[int, int]

@dataclass(frozen=True)
class PieceType:
    name: str
    value: int
    directions: List[Vector]
    sliding: bool  # True = repeat directions; False = single step

@dataclass
class Piece:
    color: int   # WHITE or BLACK
    type: PieceType

PAWN = PieceType(
    name="pawn",
    value=PAWN_VALUE,
    directions=[],   # pawn handled in Board.generate_moves_for_square
    sliding=False,
)


# Standard pieces
ROOK = PieceType(
    name="rook",
    value=5,
    directions=[(1, 0), (-1, 0), (0, 1), (0, -1)],
    sliding=True,
)

BISHOP = PieceType(
    name="bishop",
    value=3,
    directions=[(1, 1), (1, -1), (-1, 1), (-1, -1)],
    sliding=True,
)

QUEEN = PieceType(
    name="queen",
    value=9,
    directions=ROOK.directions + BISHOP.directions,
    sliding=True,
)

KNIGHT = PieceType(
    name="knight",
    value=3,
    directions=[
        (2, 1), (1, 2), (-1, 2), (-2, 1),
        (-2, -1), (-1, -2), (1, -2), (2, -1)
    ],
    sliding=False,
)

SUPER_KNIGHT = PieceType(
    name="super_knight",
    value=5,
    directions=[
        (2, 2), (-2, 2),
        (-2, -2),(2, -2), 
    ],
    sliding=False,
)

KING = PieceType(
    name="king",
    value=1000,
    directions=QUEEN.directions,
    sliding=False,
)


