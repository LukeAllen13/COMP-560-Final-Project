const API_URL = "http://127.0.0.1:8000";

// Types that match your FastAPI backend
export interface Piece {
  x: number;
  y: number;
  color: "white" | "black";
  type: string; // "rook", "pawn", "super_rook", etc.
}

export interface GameState {
  to_move: "white" | "black";
  pieces: Piece[];
  in_check?: "white" | "black" | null;
  game_over?: boolean;
  checkmate?: boolean;
  winner?: "white" | "black" | null;
}


export interface EngineMove {
  fx: number;
  fy: number;
  tx: number;
  ty: number;
}

export interface RefereeResponse {
  score: number;
  white_pieces: Record<string, number>;
  black_pieces: Record<string, number>;
  to_move: string;
  commentary: string;
}

export async function fetchState(): Promise<GameState> {
  const res = await fetch(`${API_URL}/state`);
  return await res.json();
}

export async function newGame(): Promise<GameState> {
  const res = await fetch(`${API_URL}/new-game`, {
    method: "POST",
  });
  return await res.json();
}

export async function sendMove(
  fx: number,
  fy: number,
  tx: number,
  ty: number,
  autoEngine: boolean
): Promise<{ state?: GameState; engine_move?: EngineMove; error?: string }> {
  const res = await fetch(`${API_URL}/move`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fx, fy, tx, ty, auto_engine: autoEngine }),
  });
  return await res.json();
}

export async function fetchRefereeCommentary(): Promise<RefereeResponse> {
  const res = await fetch(`${API_URL}/referee`);
  return await res.json();
}

export async function fetchEvaluation(): Promise<number> {
  const res = await fetch(`${API_URL}/evaluation`);
  const data = await res.json();
  return data.score;
}
