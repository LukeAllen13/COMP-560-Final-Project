# engine/board.py
from typing import List, Optional, Tuple, Dict, Any
from .piece_types import (
    Piece, PieceType, WHITE, BLACK,
    ROOK, BISHOP, QUEEN, KNIGHT, KING, PAWN_VALUE, SUPER_KNIGHT
)

WHITE = 1
BLACK = -1

Move = Tuple[int, int, int, int]  # (from_x, from_y, to_x, to_y)

class Board:
    def __init__(self):
        # board[y][x]
        self.board: List[List[Optional[Piece]]] = [
            [None for _ in range(8)] for _ in range(8)
        ]
        self.to_move: int = WHITE

    def clone(self) -> "Board":
        new = Board()
        new.board = [[p for p in row] for row in self.board]
        new.to_move = self.to_move
        return new
    
    def find_king(self, color: int) -> Optional[Tuple[int, int]]:
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece is not None and piece.color == color and piece.type.name == "king":
                    return (x, y)
        return None
    
    def is_square_attacked_by(self, x: int, y: int, attacker_color: int) -> bool:
        """
        Return True if square (x, y) is attacked by any piece of attacker_color.
        Simplest approach: generate all pseudo-legal moves for attacker_color,
        and see if any land on (x, y).
        """
        original_to_move = self.to_move
        self.to_move = attacker_color
        moves = self._generate_pseudo_legal_moves()
        self.to_move = original_to_move

        for fx, fy, tx, ty in moves:
            if tx == x and ty == y:
                return True
        return False

    def is_in_check(self, color: int) -> bool:
        king_pos = self.find_king(color)
        if king_pos is None:
            return False  # no king? treat as not in check
        kx, ky = king_pos
        opponent = WHITE if color == BLACK else BLACK
        return self.is_square_attacked_by(kx, ky, opponent)


    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < 8 and 0 <= y < 8

    def setup_start_position(self):
        # Clear board
        self.board = [[None for _ in range(8)] for _ in range(8)]

        # White pieces (bottom, y = 0 and 1)
        self.board[0][0] = Piece(WHITE, ROOK)
        self.board[0][1] = Piece(WHITE, KNIGHT)
        self.board[0][2] = Piece(WHITE, BISHOP)
        self.board[0][3] = Piece(WHITE, QUEEN)
        self.board[0][4] = Piece(WHITE, KING)
        self.board[0][5] = Piece(WHITE, BISHOP)
        self.board[0][6] = Piece(WHITE, SUPER_KNIGHT)
        self.board[0][7] = Piece(WHITE, ROOK)

        for x in range(8):
            # You can later make a PAWN PieceType if you want,
            # for now we just use name "pawn" via a dummy PieceType
            from .piece_types import PieceType
            PAWN_WHITE = PieceType(
                name="pawn",
                value=PAWN_VALUE,
                directions=[],   # handled specially in move gen
                sliding=False,
            )
            PAWN_BLACK = PieceType(
                name="pawn",
                value=PAWN_VALUE,
                directions=[],
                sliding=False,
            )
            # White pawns on rank 1 (y = 1)
            self.board[1][x] = Piece(WHITE, PAWN_WHITE)
            # Black pawns on rank 6 (y = 6)
            self.board[6][x] = Piece(BLACK, PAWN_BLACK)

        # Black pieces (top, y = 7 and 6)
        self.board[7][0] = Piece(BLACK, ROOK)
        self.board[7][1] = Piece(BLACK, KNIGHT)
        self.board[7][2] = Piece(BLACK, BISHOP)
        self.board[7][3] = Piece(BLACK, QUEEN)
        self.board[7][4] = Piece(BLACK, KING)
        self.board[7][5] = Piece(BLACK, BISHOP)
        self.board[7][6] = Piece(BLACK, SUPER_KNIGHT)
        self.board[7][7] = Piece(BLACK, ROOK)

        # Side to move
        self.to_move = WHITE

        # Example: drop a custom piece for testing
        # from .piece_types import SUPER_ROOK
        # self.board[3][3] = Piece(WHITE, SUPER_ROOK)

    def to_dict(self) -> Dict[str, Any]:
        pieces = []
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece is None:
                    continue
                pieces.append({
                    "x": x,
                    "y": y,
                    "color": "white" if piece.color == WHITE else "black",
                    "type": piece.type.name,
                })

        # Check status
        in_check_color: Optional[str] = None
        if self.is_in_check(WHITE):
            in_check_color = "white"
        elif self.is_in_check(BLACK):
            in_check_color = "black"

        # Game over / checkmate / winner
        legal_moves = self.generate_legal_moves()
        game_over = False
        checkmate = False
        winner: Optional[str] = None

        if len(legal_moves) == 0:
            game_over = True
            if self.is_in_check(self.to_move):
                # Checkmate: side to move is in check and has no moves
                checkmate = True
                winner = "white" if self.to_move == BLACK else "black"
            else:
                # Stalemate: no moves but not in check
                checkmate = False
                winner = None

        return {
            "to_move": "white" if self.to_move == WHITE else "black",
            "pieces": pieces,
            "in_check": in_check_color,
            "game_over": game_over,
            "checkmate": checkmate,
            "winner": winner,
        }


    def make_move(self, move: Move):
        fx, fy, tx, ty = move
        piece = self.board[fy][fx]
        assert piece is not None
        self.board[fy][fx] = None
        self.board[ty][tx] = piece
        self.to_move *= -1

    def generate_moves_for_square(self, x: int, y: int) -> List[Move]:
        moves: List[Move] = []
        piece = self.board[y][x]
        if piece is None or piece.color != self.to_move:
            return moves

        pt = piece.type

        # Non-pawn pieces:
        if pt.name != "pawn":
            for dx, dy in pt.directions:
                step = 1
                while True:
                    nx = x + dx * step
                    ny = y + dy * step
                    if not self.in_bounds(nx, ny):
                        break
                    target = self.board[ny][nx]
                    if target is None:
                        moves.append((x, y, nx, ny))
                    else:
                        if target.color != piece.color:
                            moves.append((x, y, nx, ny))
                        break
                    if not pt.sliding:
                        break
                    step += 1

        # Simple pawn movement
        if pt.name == "pawn":
            direction = 1 if piece.color == WHITE else -1
            ny = y + direction

            # forward
            if self.in_bounds(x, ny) and self.board[ny][x] is None:
                moves.append((x, y, x, ny))
                if(piece.color == WHITE):
                    if piece in self.board[1]:
                        ny2 = y + 2 * direction
                        if self.in_bounds(x, ny2) and self.board[ny2][x] is None:
                            moves.append((x, y, x, ny2))
                else:
                    if piece in self.board[6]:
                        ny2 = y + 2 * direction
                        if self.in_bounds(x, ny2) and self.board[ny2][x] is None:
                            moves.append((x, y, x, ny2))

            # captures
            for dx in (-1, 1):
                nx = x + dx
                if self.in_bounds(nx, ny):
                    target = self.board[ny][nx]
                    if target is not None and target.color != piece.color:
                        moves.append((x, y, nx, ny))

        return moves

    def _generate_pseudo_legal_moves(self) -> List[Move]:
        moves: List[Move] = []
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece is not None and piece.color == self.to_move:
                    moves.extend(self.generate_moves_for_square(x, y))
        return moves
    
    def generate_legal_moves(self) -> List[Move]:
        """True legal moves: 
        filter out those that leave our own king in check.
        """
        color_to_move = self.to_move
        legal: List[Move] = []
        
        for move in self._generate_pseudo_legal_moves():
            fx,fy,tx,ty=move
                  # Save state
            captured = self.board[ty][tx]
            piece = self.board[fy][fx]

            # Make move
            self.board[fy][fx] = None
            self.board[ty][tx] = piece

            in_check = self.is_in_check(color_to_move)

            # Undo move
            self.board[fy][fx] = piece
            self.board[ty][tx] = captured

            if not in_check:
                legal.append(move)

        return legal
