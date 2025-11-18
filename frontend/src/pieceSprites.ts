import type { Piece } from "./api";

// key format: "white_pawn", "black_queen", etc.
const spriteMap: Record<string, string> = {
  white_pawn: "/White_Pawn.png",
  white_knight: "/White_Knight.png",
  white_bishop: "/White_Bishop.png",
  white_rook: "/White_Rook.png",
  white_queen: "/White_Queen.png",
  white_king: "/White_King.png",
  white_super_knight: "/whitesuperhorse.png",
  black_pawn: "/Black_Pawn.png",
  black_knight: "/Black_Knight.png",
  black_bishop: "/Black_Bishop.png",
  black_rook: "/Black_Rook.png",
  black_queen: "/Black_Queen.png",
  black_king: "/Black_King.png",
  black_super_knight: "/blacksuperhorse.png"
};

export function getPieceSprite(piece: Piece): string | null {
  const key = `${piece.color}_${piece.type}`; // e.g. "white_pawn"
  return spriteMap[key] ?? null;
}
