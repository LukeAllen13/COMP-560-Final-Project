from .board import Board, WHITE, BLACK

def evaluate(board: Board) -> float:
    """
    Simple static evaluation function:
    Positive = better for white
    Negative = better for black

    Uses piece values from PieceType and sums color * value.
    """
    score = 0.0
    for y in range(8):
        for x in range(8):
            piece = board.board[y][x]
            if piece is None:
                continue
            value = piece.type.value
            color_factor = 1 if piece.color == WHITE else -1
            score += color_factor * value

    # Optional: treat checkmate / stalemate specially
    legal_moves = board.generate_legal_moves()
    if not legal_moves:
        if board.is_in_check(board.to_move):
            # side to move is checkmated
            mate_score = 10000
            # from White's POV: if White to move and mated → huge negative;
            # if Black to move and mated → huge positive
            return -mate_score if board.to_move == WHITE else mate_score
        else:
            # stalemate, call it equal
            return 0.0

    return score
