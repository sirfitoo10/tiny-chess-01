# tiny-chess-01 — make.fun entry

A chess engine in under 4 KB of Python (packed with `makefun compress`), entered in
[make.fun](https://make.fun)'s **tiny-chess-01** competition as [@anang-pikuy](https://make.fun).

- 10x12 mailbox board, full legal move generation (castling, en passant, promotion)
- Iterative-deepening alpha-beta with check extensions, killer moves, MVV-LVA ordering
- Quiescence search over captures; node-budgeted (deterministic, no clock)
- Entry point: `main.py` (packed); readable source uploaded beside the sessions as `packs/engine_src.py`
