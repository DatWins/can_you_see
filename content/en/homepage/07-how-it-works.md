---
title: "How It Works"
header_menu_title: "How It Works"
navigation_menu_title: "How It Works"
weight: 7
header_menu: true
---
Each game starts as a PGN file. Every game ends in checkmate. A script cuts the game into steps of a few moves, works out the answers to the questions from the real position (pawns, pieces, kings, open files, material, the mate itself) and draws the board pictures. The questions sit on flashcards you click to reveal.

The new games come from [The Week in Chess](https://theweekinchess.com/), which publishes all the week's games every Monday.

## Tools
- [Hugo flashcard shortcode](https://www.mrnice.dev/posts/hugo-flashcard-shortcode-for-study/) by Shay Nehmad — the question cards
- [python-chess](https://github.com/niklasf/python-chess) checks the positions and draws the boards: `find_mates.py` picks the checkmate games from a TWIC file, `make_test.py` turns one game into a test page
- [Hugo](https://gohugo.io/) with the [hugo-scroll](https://github.com/zjedi/hugo-scroll) theme builds the site
