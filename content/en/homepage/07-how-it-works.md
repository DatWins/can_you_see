---
title: "How It Works"
header_menu_title: "How It Works"
navigation_menu_title: "How It Works"
weight: 7
header_menu: true
---
Each game starts as a PGN file. The board pictures are drawn from it with python-chess, and the questions sit on flashcards you click to reveal.

## Tools
- [Hugo flashcard shortcode](https://www.mrnice.dev/posts/hugo-flashcard-shortcode-for-study/) by Shay Nehmad — the question cards
- [python-chess](https://github.com/niklasf/python-chess) draws the boards (`tools/can-you-see/make_boards.py`)
- [Hugo](https://gohugo.io/) with the [hugo-scroll](https://github.com/zjedi/hugo-scroll) theme builds the site
