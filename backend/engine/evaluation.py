# engine/evaluation.py
from .board import Board
from .piece_types import PAWN_VALUE

def evaluate(board: Board) -> int:
    """
    > 0 = good for White
    < 0 = good for Black
    """
    score = 0
    for y in range(8):
        for x in range(8):
            piece = board.board[y][x]
            if piece is None:
                continue
            if piece.type.name == "pawn":
                value = PAWN_VALUE
            else:
                value = piece.type.value
            score += value * piece.color
    return score
