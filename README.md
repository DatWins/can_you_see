# Can You See?

Chess visualization training: read a few moves, play them in your head, then click the question cards to check yourself.
Hugo site (hugo-scroll theme), deployed to GitHub Pages by `.github/workflows`.

## Menus
Games are grouped by length: `content/en/homepage/02-under-15.md`, `03-15-20.md`, `04-21-30.md`, `05-over-30.md`.

## Adding a game
1. Put the PGN in `tools/can-you-see/` and draw the boards (numbers are plies = half-moves):
   `py tools\can-you-see\make_boards.py tools\can-you-see\mygame.pgn static\can-you-see\mygame 12 18 24`
2. In the right length file, add the game to the `submenu` line (`"Name|anchor"`), then a `## Name {#anchor}` heading with steps:
   `{{< moves "1.e4 e5 2.Nf3" >}}` for the main-line moves, and
   `{{< flashcard question="Where are the kings?" >}}answer in Markdown{{< /flashcard >}}` for each question.
3. Board picture: `![Position after 6...Nf6](can-you-see/mygame/m12.svg)`
