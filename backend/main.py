# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from engine.board import Board, Move
from engine.search import choose_best_move

app = FastAPI()

# Allow your frontend (we'll run Vite on 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can lock this down later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single global game state (fine for class project)
game_board = Board()
game_board.setup_start_position()

class MoveRequest(BaseModel):
    fx: int
    fy: int
    tx: int
    ty: int
    auto_engine: bool = True  # default: play vs engine

@app.get("/state")
def get_state():
    """Return current board state."""
    return game_board.to_dict()

@app.post("/new-game")
def new_game():
    """Reset to starting position."""
    global game_board
    game_board = Board()
    game_board.setup_start_position()
    return game_board.to_dict()
    
@app.post("/move")
def make_move(req: MoveRequest):
    """
    Human makes a move. If auto_engine is True, the engine also replies.
    If auto_engine is False, only the human move is applied (human vs human).
    """
    global game_board
    human_move: Move = (req.fx, req.fy, req.tx, req.ty)
    legal_moves = game_board.generate_legal_moves()

    if human_move not in legal_moves:
        return {"error": "Illegal move"}

    # Apply human move
    game_board.make_move(human_move)

    engine_move_dict = None

    # Optionally let engine respond
    if req.auto_engine:
        engine_move: Optional[Move] = choose_best_move(game_board, depth=3)
        if engine_move is not None:
            game_board.make_move(engine_move)
            fx, fy, tx, ty = engine_move
            engine_move_dict = {"fx": fx, "fy": fy, "tx": tx, "ty": ty}

    return {
        "state": game_board.to_dict(),
        "engine_move": engine_move_dict,
    }
