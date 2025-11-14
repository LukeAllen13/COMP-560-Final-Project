# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import ollama

from engine.board import Board, Move
from engine.search import choose_best_move
from engine.evaluation import evaluate

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

@app.get("/referee")
def referee():
    """
    Analyze the current board state and get an AI referee's commentary.
    """
    global game_board
    
    # Get evaluation score
    score = evaluate(game_board)
    
    # Build detailed board representation with positions
    board_description = []
    white_pieces = []
    black_pieces = []
    
    for y in range(8):
        for x in range(8):
            piece = game_board.board[y][x]
            if piece is not None:
                piece_name = piece.type.name
                # Convert to chess notation (a-h, 1-8)
                file_letter = chr(ord('a') + x)
                rank_number = y + 1
                position = f"{file_letter}{rank_number}"
                
                color_name = "White" if piece.color == 1 else "Black"
                board_description.append(f"{color_name} {piece_name} on {position}")
                
                if piece.color == 1:  # WHITE
                    white_pieces.append(piece_name)
                else:  # BLACK
                    black_pieces.append(piece_name)
    
    # Create summary
    white_summary = {}
    black_summary = {}
    
    for piece in white_pieces:
        white_summary[piece] = white_summary.get(piece, 0) + 1
    
    for piece in black_pieces:
        black_summary[piece] = black_summary.get(piece, 0) + 1
    
    # Format piece counts
    white_list = ", ".join([f"{count} {name}(s)" for name, count in white_summary.items()])
    black_list = ", ".join([f"{count} {name}(s)" for name, count in black_summary.items()])
    
    # Format board positions
    positions_text = "\n".join(board_description)
    
    # Create prompt for LLM
    prompt = f"""You are a chess referee providing commentary on the current game state.

Current evaluation score: {score} (positive = white advantage, negative = black advantage)

White pieces remaining: {white_list}
Black pieces remaining: {black_list}

Whose turn: {"White" if game_board.to_move == 1 else "Black"}

Piece positions on the board:
{positions_text}

Provide a brief, engaging analysis of the current position in 2-3 sentences. Comment on material balance, who has the advantage, piece positioning and control of key squares, and any tactical or strategic observations."""

    try:
        # Call Llama 3.2 via Ollama
        response = ollama.chat(
            model='llama3.2',
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        
        commentary = response['message']['content']
        
    except Exception as e:
        commentary = f"Referee unavailable: {str(e)}"
    
    return {
        "score": score,
        "white_pieces": white_summary,
        "black_pieces": black_summary,
        "to_move": "white" if game_board.to_move == 1 else "black",
        "commentary": commentary
    }

