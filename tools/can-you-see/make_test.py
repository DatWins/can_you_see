r"""Make a "Can You See?" visualization test from one game that ends in checkmate.

Usage (Windows, from the repo folder):
    py tools\can-you-see\make_test.py mygame.pgn content\en\tests\my-game

It writes  content\en\tests\my-game\index.md  (the page), the board pictures (m###.svg)
and a copy of the game (game.pgn). Every answer is worked out from the real position
by python-chess, so the tables are always right.
Needs:  py -m pip install chess

The game is cut into steps: 3 moves per step for games up to 20 moves,
4 moves for 21-30, 5 moves for longer games (the mating move is kept back
for the final question).
"""
import sys, pathlib
import chess, chess.pgn, chess.svg

NAME = {1: "pawn", 2: "knight", 3: "bishop", 4: "rook", 5: "queen", 6: "king"}
PLURAL = {1: "pawns", 2: "knights", 3: "bishops", 4: "rooks", 5: "queens", 6: "kings"}
ROW = {1: "Pawns", 2: "Knights", 3: "Bishops", 4: "Rooks", 5: "Queen", 6: "King"}
LETTER = {2: "N", 3: "B", 4: "R", 5: "Q"}
VALUE = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9}
SIDE = {chess.WHITE: "White", chess.BLACK: "Black"}
START = {1: 8, 2: 2, 3: 2, 4: 2, 5: 1}
COLORS = {"square light": "#f0d9b5", "square dark": "#b58863",
          "square light lastmove": "#cdd26a", "square dark lastmove": "#aaa23a",
          "margin": "#3b2416", "coord": "#f0d9b5"}


def sq_sorted(squares):
    return sorted(squares, key=lambda s: (chess.square_file(s), chess.square_rank(s)))


def names(squares):
    return " ".join(chess.square_name(s) for s in sq_sorted(squares))


def piece_list(board, color, squares):
    """'knight f3, bishop c4' for the given squares, strongest piece first."""
    items = sorted(squares, key=lambda s: (-board.piece_type_at(s), chess.square_file(s)))
    return ", ".join(f"{NAME[board.piece_type_at(s)]} **{chess.square_name(s)}**" for s in items)


def fmt_moves(sans, first_ply):
    out = []
    for i, san in enumerate(sans):
        p = first_ply + i
        n = p // 2 + 1
        if p % 2 == 0:
            out.append(f"{n}.{san}")
        elif i == 0:
            out.append(f"{n}...{san}")
        else:
            out.append(san)
    return " ".join(out)


def board_svg(board, move):
    arrows = [chess.svg.Arrow(move.from_square, move.to_square, color="#2f6b3acc")] if move else []
    check = board.king(board.turn) if board.is_check() else None
    return chess.svg.board(board, size=360, lastmove=move, coordinates=True, colors=COLORS,
                           arrows=arrows, check=check)


class Tracker:
    """Follows the game and remembers which pieces have never moved and who castled."""
    def __init__(self):
        self.board = chess.Board()
        self.untouched = set(chess.SquareSet(self.board.occupied))
        self.castled = {chess.WHITE: None, chess.BLACK: None}

    def push(self, move):
        b = self.board
        san = b.san(move)
        captured = None
        if b.is_capture(move):
            if b.is_en_passant(move):
                captured = (1, move.to_square)
            else:
                captured = (b.piece_type_at(move.to_square), move.to_square)
        if b.is_castling(move):
            self.castled[b.turn] = "kingside" if b.is_kingside_castling(move) else "queenside"
            rank = 0 if b.turn else 7
            rook_file = 7 if b.is_kingside_castling(move) else 0
            self.untouched.discard(chess.square(rook_file, rank))
        mover = b.turn
        self.untouched.discard(move.from_square)
        self.untouched.discard(move.to_square)
        b.push(move)
        return san, captured, mover


# ---------- answers ----------

def ans_pawns(b):
    rows = ["| | Pawns (moved ones in **bold**) | Count |", "|---|---|---|"]
    for c in (chess.WHITE, chess.BLACK):
        home = 1 if c else 6
        ps = sq_sorted(b.pieces(chess.PAWN, c))
        txt = " ".join(f"**{chess.square_name(s)}**" if chess.square_rank(s) != home else chess.square_name(s)
                       for s in ps) or "—"
        rows.append(f"| {SIDE[c]} | {txt} | {len(ps)} |")
    center = []
    for c in (chess.WHITE, chess.BLACK):
        cs = [s for s in b.pieces(chess.PAWN, c) if chess.square_file(s) in (2, 3, 4, 5)
              and 2 <= chess.square_rank(s) <= 5]
        center.append(f"{SIDE[c]} {names(cs)}" if cs else f"{SIDE[c]} none")
    return "\n".join(rows) + f"\n\nIn the center (c- to f-files, ranks 3–6): {'; '.join(center)}."


def gone(b, c):
    out = []
    for pt in (5, 4, 3, 2, 1):
        n = START[pt] - len(b.pieces(pt, c))
        if n > 0:
            out.append(f"{n} {PLURAL[pt] if n > 1 else NAME[pt]}")
    return ", ".join(out)


def ans_out(t):
    b = t.board
    lines = []
    for c in (chess.WHITE, chess.BLACK):
        moved = [s for s in chess.SquareSet(b.occupied_co[c])
                 if b.piece_type_at(s) not in (chess.PAWN,) and s not in t.untouched]
        lines.append(f"**{SIDE[c]}:** {piece_list(b, c, moved) if moved else 'nothing yet'}.")
    g = [f"{SIDE[c]} has lost {gone(b, c)}" for c in (chess.WHITE, chess.BLACK) if gone(b, c)]
    if g:
        lines.append("Gone from the board: " + "; ".join(g) + ".")
    return "\n\n".join(lines)


def ans_kings(t):
    b = t.board
    out = []
    for c in (chess.WHITE, chess.BLACK):
        k = chess.square_name(b.king(c))
        how = f"castled {t.castled[c]}" if t.castled[c] else (
            "still on its starting square, not castled" if b.king(c) in t.untouched else "has moved, never castled")
        out.append(f"**{SIDE[c]} king: {k}** — {how}.")
    return "\n\n".join(out)


def ans_files(b):
    opn, half = [], {chess.WHITE: [], chess.BLACK: []}
    for f in range(8):
        w = any(chess.square_file(s) == f for s in b.pieces(chess.PAWN, chess.WHITE))
        k = any(chess.square_file(s) == f for s in b.pieces(chess.PAWN, chess.BLACK))
        fn = chess.FILE_NAMES[f]
        if not w and not k:
            opn.append(fn)
        elif not w:
            half[chess.WHITE].append(fn)
        elif not k:
            half[chess.BLACK].append(fn)
    parts = []
    parts.append(("**Open files** (no pawns at all): " + ", ".join(f"{x}-file" for x in opn) + ".")
                 if opn else "**No file is fully open** — every file still has a pawn on it.")
    for c in (chess.WHITE, chess.BLACK):
        if half[c]:
            parts.append(f"Half open for {SIDE[c]} (only a {SIDE[not c]} pawn on it): "
                         + ", ".join(f"{x}-file" for x in half[c]) + ".")
    rooks = []
    for c in (chess.WHITE, chess.BLACK):
        for s in b.pieces(chess.ROOK, c) | b.pieces(chess.QUEEN, c):
            if chess.FILE_NAMES[chess.square_file(s)] in opn:
                rooks.append(f"{SIDE[c]} {NAME[b.piece_type_at(s)]} {chess.square_name(s)}")
    if rooks:
        parts.append("Already on an open file: " + ", ".join(rooks) + ".")
    return "\n\n".join(parts)


def ans_unmoved(t):
    b = t.board
    out = []
    for c in (chess.WHITE, chess.BLACK):
        sq = [s for s in t.untouched if b.color_at(s) == c and b.piece_type_at(s) != chess.PAWN]
        ps = [s for s in t.untouched if b.color_at(s) == c and b.piece_type_at(s) == chess.PAWN]
        txt = piece_list(b, c, sq) if sq else "none — every piece has moved"
        out.append(f"**{SIDE[c]}:** {txt}. Pawns still at home: {names(ps) or 'none'}.")
    return "\n\n".join(out)


def material(b, c):
    parts, pts = [], 0
    for pt in (5, 4, 3, 2):
        n = len(b.pieces(pt, c))
        pts += n * VALUE[pt]
        if n:
            parts.append(f"{n if n > 1 else ''}{LETTER[pt]}")
    n = len(b.pieces(1, c)); pts += n
    parts.append(f"{n} pawn{'s' if n != 1 else ''}")
    return ", ".join(parts), pts


def ans_material(b):
    w, wp = material(b, chess.WHITE)
    k, kp = material(b, chess.BLACK)
    d = wp - kp
    verdict = "**Material is equal.**" if d == 0 else \
        f"**{'White' if d > 0 else 'Black'} is ahead by {abs(d)} point{'s' if abs(d) != 1 else ''}.**"
    return (f"{verdict}\n\n| | Pieces | Points |\n|---|---|---|\n| White | {w} | {wp} |\n| Black | {k} | {kp} |\n\n"
            "(Pawn 1, knight 3, bishop 3, rook 5, queen 9.)")


def ans_table(b, img):
    rows = ["| | White | Black |", "|---|---|---|"]
    for pt in (1, 2, 3, 4, 5, 6):
        cells = [names(b.pieces(pt, c)) or "—" for c in (chess.WHITE, chess.BLACK)]
        rows.append(f"| {ROW[pt]} | {cells[0]} | {cells[1]} |")
    return "\n".join(rows) + f"\n\n![Check your picture]({img})"


def ans_corner(b, c):
    k = b.king(c)
    near = [s for s in chess.SquareSet(chess.BB_ALL) if s != k and chess.square_distance(s, k) <= 2]
    own = [s for s in near if b.color_at(s) == c]
    foe = [s for s in near if b.color_at(s) == (not c)]
    lines = [f"{SIDE[c]}'s king is on **{chess.square_name(k)}**."]
    lines.append(f"Its own pieces close by: {piece_list(b, c, own) if own else 'none'}.")
    lines.append(f"{SIDE[not c]} pieces close by: {piece_list(b, not c, foe) if foe else 'none'}.")
    eyed = []
    for s in sq_sorted(chess.SquareSet(chess.BB_KING_ATTACKS[k])):
        att = b.attackers(not c, s)
        if att:
            eyed.append(f"{chess.square_name(s)} ({', '.join(f'{NAME[b.piece_type_at(a)]} {chess.square_name(a)}' for a in att)})")
    lines.append(f"Squares next to the king that {SIDE[not c]} already hits: "
                 + ("; ".join(eyed) if eyed else "none") + ".")
    return "\n\n".join(lines)


def ans_captures(caps):
    return "\n\n".join(f"**{m}** took a {NAME[pt]} on {chess.square_name(sq)}." for m, pt, sq in caps)


def and_join(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def who(b, squares):
    return and_join([f"the {NAME[b.piece_type_at(a)]} on {chess.square_name(a)}" for a in sq_sorted(squares)])


def pinner(b, color, sq):
    """The enemy piece that pins the piece on sq to its king."""
    ray = b.pin(color, sq)
    for s in ray:
        if b.color_at(s) == (not color) and s != sq:
            return s
    return None


def ans_mate(b, san):
    mover, loser = not b.turn, b.turn
    k = b.king(loser)
    checkers = list(b.checkers())
    out = [f"Check from {who(b, checkers)}" +
           (" — a **double check**, so the king must move." if len(checkers) > 1 else ".")]
    tmp = b.copy(); tmp.remove_piece_at(k)
    flight = []
    for s in sq_sorted(chess.SquareSet(chess.BB_KING_ATTACKS[k])):
        p = b.piece_at(s)
        att = tmp.attackers(mover, s)
        if p and p.color == loser:
            flight.append(f"- **{chess.square_name(s)}** — blocked by its own {NAME[p.piece_type]}")
        elif p:
            flight.append(f"- **{chess.square_name(s)}** — the {SIDE[mover]} {NAME[p.piece_type]} stands there, "
                          f"protected by {who(b, att)}")
        else:
            flight.append(f"- **{chess.square_name(s)}** — covered by {who(b, att)}")
    out.append(f"The {SIDE[loser]} king on {chess.square_name(k)} has no square to go to:\n\n" + "\n".join(flight))
    if len(checkers) == 1:
        cs = checkers[0]; cn = NAME[b.piece_type_at(cs)]
        takers = [s for s in b.attackers(loser, cs) if s != k]
        guards = b.attackers(mover, cs)
        lines = []
        if k in b.attackers(loser, cs) and guards:
            lines.append(f"The king can't take the {cn} — it is protected by {who(b, guards)}.")
        for s in sq_sorted(takers):
            pn = pinner(b, loser, s)
            if pn is not None:
                lines.append(f"The {NAME[b.piece_type_at(s)]} on {chess.square_name(s)} could take it, but it is "
                             f"**pinned** to its king by the {NAME[b.piece_type_at(pn)]} on {chess.square_name(pn)}.")
        if not lines:
            lines.append(f"Nothing can take the {cn}.")
        between = chess.SquareSet(chess.between(cs, k))
        if between:
            lines.append(f"Nothing can step in between on {names(between)}.")
        out.append(" ".join(lines))
    return "\n\n".join(out)


# ---------- page ----------

def card(q, a):
    return f'{{{{< flashcard question="{q}" >}}}}\n{a}\n{{{{< /flashcard >}}}}\n'


def make(pgn_path, out_dir):
    game = chess.pgn.read_game(open(pgn_path, encoding="utf-8", errors="replace"))
    moves = list(game.mainline_moves())
    h = game.headers
    end = game.board()
    for m in moves:
        end.push(m)
    if not end.is_checkmate():
        sys.exit("This game does not end in checkmate.")
    P = len(moves)
    nmoves = (P + 1) // 2
    step = 6 if nmoves <= 20 else 8 if nmoves <= 30 else 10
    bounds, a = [], 0
    while a < P - 1:
        bounds.append((a, min(a + step, P - 1))); a += step
    if len(bounds) > 1 and bounds[-1][1] - bounds[-1][0] < 3:
        bounds[-2] = (bounds[-2][0], bounds[-1][1]); bounds.pop()

    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    (out / "game.pgn").write_text(str(game) + "\n", encoding="utf-8")
    loser = end.turn
    winner = not loser
    t = Tracker()
    md = []
    extras = ["material", "kings", "files", "unmoved", "corner", "captures"]
    for k, (a, z) in enumerate(bounds):
        sans, caps, last = [], [], None
        for p in range(a, z):
            san, cap, mover = t.push(moves[p]); sans.append(san); last = moves[p]
            if cap:
                caps.append((fmt_moves([san], p), cap[0], cap[1]))
        b = t.board
        first_n, last_n = a // 2 + 1, (z - 1) // 2 + 1
        rng = f"Move {first_n}" if first_n == last_n else f"Moves {first_n}–{last_n}"
        md.append(f"### Step {k + 1} · {rng}\n\n{{{{< moves \"{fmt_moves(sans, a)}\" >}}}}\n")
        img = f"m{z:03d}.svg"
        (out / img).write_text(board_svg(b, last), encoding="utf-8")
        final = k == len(bounds) - 1
        if k == 0:
            md.append(card("What does the pawn structure look like?", ans_pawns(b)))
            md.append(card("Which pieces have been brought out?", ans_out(t)))
        elif k == 1:
            md.append(card("What does the pawn structure look like now?", ans_pawns(b)))
            md.append(card("Which pieces have been brought out?", ans_out(t)))
            md.append(card("Where are the kings?", ans_kings(t)))
            md.append(card("Which files are open?", ans_files(b)))
            md.append(f"**Check your picture** — the position after {fmt_moves(sans[-1:], z - 1)}:\n\n![Position]({img})\n")
        else:
            md.append(card("Where is every piece? Pawns, knights, bishops, rooks, queen, king.", ans_table(b, img)))
            picks = ["material", "corner"] if final else [extras[(2 * k) % 6], extras[(2 * k + 1) % 6]]
            if "captures" in picks and not caps:
                picks[picks.index("captures")] = "unmoved" if "unmoved" not in picks else "files"
            for x in picks:
                if x == "material":
                    md.append(card("What is the material situation? Who is ahead?", ans_material(b)))
                elif x == "kings":
                    md.append(card("Where are the kings? Has anyone castled?", ans_kings(t)))
                elif x == "files":
                    md.append(card("Which files are open?", ans_files(b)))
                elif x == "unmoved":
                    md.append(card("Which pieces haven't moved from their starting squares?", ans_unmoved(t)))
                elif x == "corner":
                    md.append(card(f"Look at the corner around {SIDE[loser]}'s king. What is near it?", ans_corner(b, loser)))
                elif x == "captures":
                    md.append(card("What was captured in these moves?", ans_captures(caps)))
    mate_san, _, _ = t.push(moves[-1])
    (out / f"m{P:03d}.svg").write_text(board_svg(t.board, moves[-1]), encoding="utf-8")
    md.append("### Final question\n")
    md.append(card(f"{SIDE[winner]} to move. What is the checkmate?",
                   f"{{{{< moves \"{fmt_moves([mate_san], P - 1)}\" >}}}}\n\n{ans_mate(t.board, mate_san)}\n\n![Final position](m{P:03d}.svg)"))

    white, black = h.get("White", "?"), h.get("Black", "?")
    def elo(x):
        v = h.get(x, "")
        return f" ({v})" if v.isdigit() else ""
    title = f"{white.replace(',', ', ').replace(',  ', ', ')} – {black.replace(',', ', ').replace(',  ', ', ')}"
    info = (f"{white}{elo('WhiteElo')} – {black}{elo('BlackElo')} · {h.get('Event', '')}, round {h.get('Round', '?')}, "
            f"{h.get('Date', '').replace('.??', '')}. The game ends in checkmate on move {nmoves}. "
            f"[Download the PGN](game.pgn)")
    front = (f'---\ntitle: "{title}"\nmoves: {nmoves}\nevent: "{h.get("Event", "")}"\n'
             f'gamedate: "{h.get("Date", "").replace(".??", "")}"\n---\n')
    intro = ("Read each step's moves, play them **in your head** (no board!), then click the cards to check yourself. "
             "Board pictures only appear inside the answers — and once, after step 2.\n")
    page = front + info + "\n\n" + intro + "\n{{< flashcard-all >}}\n\n" + "\n".join(md)
    (out / "index.md").write_text(page, encoding="utf-8")
    print(f"{out}: {nmoves} moves, {len(bounds)} steps")


if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2])
