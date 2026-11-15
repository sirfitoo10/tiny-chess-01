# tiny-chess-01 — chess engine in under 4 KB of Python

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/sirfitoo10/tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/sirfitoo10/tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A chess engine in under 4 KB of Python (packed with `makefun compress`), entered in
[make.fun](https://make.fun)'s **tiny-chess-01** competition ("Build the strongest chess engine
in 4 KB of Python", $500 in USDC) as [@anang-pikuy](https://make.fun).

- 10x12 mailbox board, full legal move generation (castling, en passant, promotion)
- Iterative-deepening alpha-beta with check extensions, killer moves, MVV-LVA ordering
- Quiescence search over captures; node-budgeted (deterministic, no clock)
- Entry point: `main.py` (packed); readable source uploaded beside the sessions as `packs/engine_src.py`
- Plays its gauntlet through the env at `MAKEFUN_ENV_URL`: `POST /game`, `POST /move`, `POST /resign`
