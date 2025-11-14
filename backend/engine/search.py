# engine/search.py
import math
from typing import Optional
from .board import Board, Move
from .evaluation import evaluate

def minimax(board: Board, depth: int, alpha: float, beta: float) -> int:
    if depth == 0:
        return evaluate(board)

    moves = board.generate_legal_moves()
    if not moves:
        # No moves: treat as draw (0) for now.
        return 0

    if board.to_move == 1:  # WHITE
        value = -math.inf
        for move in moves:
            child = board.clone()
            child.make_move(move)
            value = max(value, minimax(child, depth - 1, alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:  # BLACK
        value = math.inf
        for move in moves:
            child = board.clone()
            child.make_move(move)
            value = min(value, minimax(child, depth - 1, alpha, beta))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

def choose_best_move(board: Board, depth: int) -> Optional[Move]:
    moves = board.generate_legal_moves()
    if not moves:
        return None

    best_move = None
    if board.to_move == 1:  # WHITE
        best_value = -math.inf
        for move in moves:
            child = board.clone()
            child.make_move(move)
            value = minimax(child, depth - 1, -math.inf, math.inf)
            if value > best_value:
                best_value = value
                best_move = move
    else:  # BLACK
        best_value = math.inf
        for move in moves:
            child = board.clone()
            child.make_move(move)
            value = minimax(child, depth - 1, -math.inf, math.inf)
            if value < best_value:
                best_value = value
                best_move = move

    return best_move
