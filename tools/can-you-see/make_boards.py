r"""Draw the 'Can You See?' board pictures for one game.

Usage (Windows):  py make_boards.py opera_game.pgn ..\..\static\can-you-see\opera 12 18 24 32 33
The numbers are PLIES (half-moves): 12 = after Black's 6th move, 33 = after White's 17th.
Each picture is saved as  m<ply>.svg  with a green arrow on the move just played.
Needs:  py -m pip install chess
"""
import sys, pathlib
import chess, chess.pgn, chess.svg

COLORS = {"square light": "#f0d9b5", "square dark": "#b58863",
          "square light lastmove": "#cdd26a", "square dark lastmove": "#aaa23a",
          "margin": "#3b2416", "coord": "#f0d9b5"}

pgn, out, *plies = sys.argv[1:]
out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
game = chess.pgn.read_game(open(pgn, encoding="utf-8"))
board, wanted = game.board(), {int(p) for p in plies}
for ply, move in enumerate(game.mainline_moves(), start=1):
    board.push(move)
    if ply in wanted:
        svg = chess.svg.board(board, size=360, lastmove=move, coordinates=True, colors=COLORS,
                              arrows=[chess.svg.Arrow(move.from_square, move.to_square, color="#2f6b3acc")],
                              check=board.king(board.turn) if board.is_check() else None)
        (out / f"m{ply:02d}.svg").write_text(svg, encoding="utf-8")
        print("saved", out / f"m{ply:02d}.svg")
