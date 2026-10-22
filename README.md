# Can You See?

Chess visualization training: read a few moves, play them in your head, then click the question cards to check yourself.
Hugo site (hugo-scroll theme), deployed to GitHub Pages by `.github/workflows`.

## Menus
Games are grouped by length: `content/en/homepage/02-10-moves.md`, `03-10-15.md`, `04-15-20.md`, `05-21-30.md`, `06-over-30.md`.

## Adding games from a TWIC week
Needs Python and `py -m pip install chess`. From the repo folder:

1. Find the games that end in checkmate (every mate up to 20 moves, plus the 6 strongest of 21–30 and of 31–45 moves):
   `py tools\can-you-see\find_mates.py twic1668.pgn picked`
2. Make a test page for each game:
   `py tools\can-you-see\make_test.py picked\firouzja-arslanov.pgn content\en\tests\firouzja-arslanov`
3. Commit and push. Each test appears by itself in the right length menu (10 Moves, 10–15, 15–20, 21–30, Over 30).

Each test lives in `content/en/tests/<name>/` (`index.md`, board pictures, `game.pgn`).
