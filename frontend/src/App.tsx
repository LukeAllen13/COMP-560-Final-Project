import { useEffect, useState } from "react";
import "./App.css";
import { fetchState, newGame, sendMove, fetchRefereeCommentary, fetchEvaluation, type GameState, type Piece } from "./api";
import { getPieceSprite } from "./pieceSprites";

function App() {
  const [state, setState] = useState<GameState | null>(null);
  const [selected, setSelected] = useState<{ x: number; y: number } | null>(null);
  const [error, setError] = useState("");
  const [showGameOver, setShowGameOver] = useState(false);
  const [vsEngine, setVsEngine] = useState(true); // true = engine replies, false = two-player
  const [moveCount, setMoveCount] = useState(0);
  const [refereeCommentary, setRefereeCommentary] = useState<string | null>(null);
  const [showCommentary, setShowCommentary] = useState(false);
  const [isLoadingCommentary, setIsLoadingCommentary] = useState(false);
  const [evaluationScore, setEvaluationScore] = useState(0);


  useEffect(() => {
    fetchState().then(setState);
    fetchEvaluation().then(setEvaluationScore);
  }, []);

  useEffect(() => {
  if (state?.game_over) {
    setShowGameOver(true);
  } else {
    setShowGameOver(false);
  }
}, [state?.game_over]);


  const handleNewGame = async () => {
    const s = await newGame();
    setState(s);
    setSelected(null);
    setError("");
    setMoveCount(0);
    setRefereeCommentary(null);
    setShowCommentary(false);
    setEvaluationScore(0);
  };

  const handleSquareClick = async (x: number, y: number) => {
    if (!state) return;
    if (state.game_over) return; // no moves after game is over

    // First click = select a piece
    if (!selected) {
      const piece = state.pieces.find((p) => p.x === x && p.y === y);
      if (!piece) return;
      setSelected({ x, y });
      setError("");
      return;
    }

    // Second click = attempt move
    const fx = selected.x;
    const fy = selected.y;
    const tx = x;
    const ty = y;

    try {
      const result = await sendMove(fx, fy, tx, ty, vsEngine);
      if (result.error) {
        setError(result.error);
      } else if (result.state) {
        setState(result.state);
        setError("");
        
        // Update evaluation score
        fetchEvaluation().then(setEvaluationScore);
        
        // Count moves: +1 for player, +1 for engine if it moved
        const movesThisTurn = result.engine_move ? 2 : 1;
        const newMoveCount = moveCount + movesThisTurn;
        setMoveCount(newMoveCount);
        
        // Check if we should fetch referee commentary (every 5 moves)
        if (newMoveCount % 5 === 0) {
          setIsLoadingCommentary(true);
          setShowCommentary(true);
          try {
            const refereeData = await fetchRefereeCommentary();
            setRefereeCommentary(refereeData.commentary);
          } catch (err) {
            setRefereeCommentary("Unable to fetch commentary at this time.");
          } finally {
            setIsLoadingCommentary(false);
          }
        }
      }
    } catch {
      setError("Network error");
    }

    setSelected(null);
  };

  if (!state) {
    return <div className="app">Loading...</div>;
  }
return (
  <div className="app">
    <h1>Chessly</h1>

    <label style={{ display: "block", marginBottom: "8px" }}>
      <input
        type="checkbox"
        checked={vsEngine}
        onChange={(e) => setVsEngine(e.target.checked)}
      />
      {" "}Play vs engine
    </label>

    <button onClick={handleNewGame}>New Game</button>
    {error && <p className="error">{error}</p>}

    <AdvantageBar score={evaluationScore} />

    <Board
      state={state}
      selected={selected}
      onSquareClick={handleSquareClick}
    />

    <p>To move: {state.to_move}</p>
    <p className="move-count">Total moves: {moveCount}</p>

    
    {state.in_check && !state.game_over && (
  <p className="check-text">
    {state.in_check === "white" ? "White is in check!" : "Black is in check!"}
  </p>
)}

{showCommentary && (
  <div className="commentary-bubble">
    <div className="commentary-header">
      <span className="commentary-title">🎙️ Referee Commentary</span>
      <button 
        className="commentary-close"
        onClick={() => setShowCommentary(false)}
      >
        ×
      </button>
    </div>
    <div className="commentary-content">
      {isLoadingCommentary ? (
        <p className="commentary-loading">Analyzing position...</p>
      ) : (
        <p>{refereeCommentary}</p>
      )}
    </div>
  </div>
)}

{state.game_over && showGameOver && (
  <div className="game-over-overlay">
    <div className="game-over-panel">
      <h2 className="game-over-title">
        {state.winner
          ? `${state.winner[0].toUpperCase() + state.winner.slice(1)} wins!`
          : "Draw"}
      </h2>
      {state.checkmate && <p className="checkmate-text">Checkmate</p>}
      <button
        className="game-over-dismiss"
        onClick={() => setShowGameOver(false)}
      >
        Dismiss
      </button>
    </div>
  </div>
)}
  </div>
  
);


interface AdvantageBarProps {
  score: number;
}

function AdvantageBar({ score }: AdvantageBarProps) {
  // Clamp the score to a reasonable range for visualization (-10 to +10)
  const maxScore = 10;
  const clampedScore = Math.max(-maxScore, Math.min(maxScore, score));
  
  // Calculate percentages (50% is even, shift based on score)
  const whitePercent = 50 + (clampedScore / maxScore) * 50;
  const blackPercent = 100 - whitePercent;
  
  return (
    <div className="advantage-bar-container">
      <div className="advantage-bar-label">
        <span className="white-label">White</span>
        <span className="score-display">{score > 0 ? "+" : ""}{score.toFixed(1)}</span>
        <span className="black-label">Black</span>
      </div>
      <div className="advantage-bar">
        <div 
          className="advantage-bar-white"
          style={{ width: `${whitePercent}%` }}
        />
        <div 
          className="advantage-bar-black"
          style={{ width: `${blackPercent}%` }}
        />
      </div>
    </div>
  );
}

interface BoardProps {
  state: GameState;
  selected: { x: number; y: number } | null;
  onSquareClick: (x: number, y: number) => void;
}

function Board({ state, selected, onSquareClick }: BoardProps) {
  const squares = [];

  for (let y = 7; y >= 0; y--) {
    for (let x = 0; x < 8; x++) {
      const piece = state.pieces.find((p) => p.x === x && p.y === y);
      const isSelected = selected?.x === x && selected?.y === y;

      squares.push(
        <Square
          key={`${x}-${y}`}
          x={x}
          y={y}
          piece={piece}
          selected={!!isSelected}
          onClick={() => onSquareClick(x, y)}
        />
      );
    }
  }

  return <div className="board">{squares}</div>;
}

interface SquareProps {
  x: number;
  y: number;
  piece?: Piece;
  selected: boolean;
  onClick: () => void;
}

function Square({ x, y, piece, selected, onClick }: SquareProps) {
  const isDark = (x + y) % 2 === 1;
  const className =
    "square" +
    (isDark ? " dark" : " light") +
    (selected ? " selected" : "");

  return (
  <div className={className} onClick={onClick}>
    {piece && <PieceImage piece={piece} />}
  </div>
);

}
function PieceImage({ piece }: { piece: Piece }) {
  const src = getPieceSprite(piece);
  if (!src) {
    // fallback to letter if we don't have an image (e.g. future custom piece)
    return <span>{pieceSymbol(piece)}</span>;
  }
  return (
    <img
      src={src}
      alt={`${piece.color} ${piece.type}`}
      className="piece-img"
    />
  );
}

function pieceSymbol(piece: Piece): string {
  const map: Record<string, string> = {
    king: "K",
    queen: "Q",
    rook: "R",
    bishop: "B",
    knight: "N",
    pawn: "P",
    super_rook: "S", // example custom piece
  };
  let ch = map[piece.type] || "?";
  if (piece.color === "black") ch = ch.toLowerCase();
  return ch;
}
}
export default App;

