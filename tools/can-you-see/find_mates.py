r"""Find the games that end in checkmate in a big PGN file (for example a TWIC weekly download).

Usage (Windows, from the repo folder):
    py tools\can-you-see\find_mates.py twic1667.pgn picked

It prints how many mates there are in each length group, then saves the picked games
as one PGN file each in the folder "picked", named after the players:
  - every mate of 20 moves or fewer
  - the 6 strongest mates (highest average rating) of 21-30 moves and of 31-45 moves,
    choosing slow games first (blitz and Titled Tuesday games only if there are not enough)
Then make the tests with make_test.py, for example:
    py tools\can-you-see\make_test.py picked\firouzja-arslanov.pgn content\en\tests\firouzja-arslanov
Needs:  py -m pip install chess
"""
import sys, re, pathlib, unicodedata
import chess, chess.pgn

PER_GROUP = 6


def is_blitz(h):
    tc, ev = h.get("TimeControl", ""), h.get("Event", "")
    secs = re.match(r"^(\d+)$", tc)            # "300" = seconds
    mins = re.match(r"^(\d+)\+\d+$", tc)       # "3+2" or "90+30" = minutes + increment
    if (secs and int(secs.group(1)) <= 600) or (mins and int(mins.group(1)) <= 10):
        return True
    return any(w in ev for w in ("Titled", "3-0", "Blitz", "Bullet", "Rapid"))


def elo(h, k):
    v = h.get(k, "")
    return int(v) if v.isdigit() else 0


def surname(name):
    s = name.split(",")[0].strip()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "player"


def main(src, dest):
    mates = []
    with open(src, encoding="utf-8", errors="replace") as f:
        while True:
            g = chess.pgn.read_game(f)
            if g is None:
                break
            b = g.board()
            try:
                for m in g.mainline_moves():
                    b.push(m)
            except Exception:
                continue
            if b.is_checkmate():
                mates.append(((b.ply() + 1) // 2, g))
    groups = {"10 moves or fewer": (0, 10), "11-15 moves": (11, 15), "16-20 moves": (16, 20),
              "21-30 moves": (21, 30), "31-45 moves": (31, 45), "over 45 moves": (46, 999)}
    for name, (lo, hi) in groups.items():
        print(f"{name:>18}: {sum(lo <= n <= hi for n, _ in mates)}")
    picked = [g for n, g in mates if n <= 20]
    for lo, hi in ((21, 30), (31, 45)):
        pool = [g for n, g in mates if lo <= n <= hi]
        pool.sort(key=lambda g: (is_blitz(g.headers), -(elo(g.headers, "WhiteElo") + elo(g.headers, "BlackElo"))))
        picked += pool[:PER_GROUP]
    out = pathlib.Path(dest); out.mkdir(parents=True, exist_ok=True)
    for g in picked:
        h = g.headers
        slug = f"{surname(h.get('White', ''))}-{surname(h.get('Black', ''))}"
        path = out / f"{slug}.pgn"
        i = 2
        while path.exists():
            path = out / f"{slug}-{i}.pgn"; i += 1
        path.write_text(str(g) + "\n", encoding="utf-8")
    print(f"saved {len(picked)} games in {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
