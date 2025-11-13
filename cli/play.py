# cli/play.py
from engine.board import Board
from engine.search import choose_best_move

def print_board(board: Board):
    for y in range(7, -1, -1):
        row = []
        for x in range(8):
            piece = board.board[y][x]
            if piece is None:
                row.append(".")
            else:
                symbol = piece.type.name[0].upper()
                if piece.color == -1:
                    symbol = symbol.lower()
                row.append(symbol)
        print(" ".join(row))
    print()

def main():
    b = Board()
    b.setup_start_position()

    while True:
        print_board(b)
        moves = b.generate_legal_moves()
        if not moves:
            print("No moves, game over.")
            break

        if b.to_move == 1:  # White = human
            user = input("Enter move as fx fy tx ty (or 'q'): ")
            if user == "q":
                break
            fx, fy, tx, ty = map(int, user.split())
            move = (fx, fy, tx, ty)
            if move not in moves:
                print("Illegal move")
                continue
            b.make_move(move)
        else:  # Black = engine
            print("Engine thinking...")
            move = choose_best_move(b, depth=3)
            if move is None:
                print("Engine has no moves.")
                break
            b.make_move(move)

if __name__ == "__main__":
    main()
