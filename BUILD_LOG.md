# BUILD_LOG.md — btc-race-24h-20261115-0828

Built 2026-11-15 ~19:00–19:20 WIB by a worker subagent (standing
authorization: build + submit make.fun entries automatically; this run
covers build only — repo creation, push, bundle, check and submit are the
parent's steps).

## Steps

1. Read `RULES.txt` and `competition.yaml` in full from the kit at
   `~/workspace/makefun/kits/btc-race-24h-20261115-0828/unpacked/btc-race-24h-20261115-0828-kit/`.
   Key facts: 1-minute cbBTC bars, $1,000 paper, long only, protocol
   `agent-fun/bars-replay/v1`, fee 4 bps + slippage 2 bps + pool impact,
   dev gate net PnL > $0, guardrails ≥1 trade and max DD ≤ 25%.
2. Read the kit's Python SDK shim (`sdk/makefun_bars.py`), the
   `ema-cross` and `rsi-bollinger` baselines, and the harness fill math
   (`harness/sim/bars/engine.ts`: `BarsPool`, `barsBuyFill`,
   `barsSellFill`, decision checks, flatten).
3. Dev window inspection: 1,440 bars, 0 gaps, BTC −4.00% (67,215.60 →
   64,523.80), 1-minute return stdev ~12 bps, 57 flat bars.
4. Built an exact integer replica of the engine's fill math
   (`/tmp/btc-sim/sim.py`) and grid-searched four families (EMA cross,
   RSI/Bollinger, breakout, dip-buy). Dip-buying won; the 60-bar
   lookback / 210–275 bps drop / 75–100 bps trail region is a broad
   positive plateau.
5. Implemented the winner in `main.py` (integer arithmetic only) with the
   kit SDK shim vendored byte-identical under `vendor/` (sha256
   `80452b00d2eb1e9c959e73d41cda6ca726cdbe7bfa4065d48278c22eccd276ff`).
6. Drove the real `main.py` subprocess through the protocol over the full
   dev dataset with the exact engine math (`/tmp/btc-sim/drive.py`):
   run 1 and run 2 both give net PnL **+$29.18**, 8 trades, max DD
   1.92%, and byte-identical reply streams (sha256
   `f045cc64d0e0696768aeeb2ce4560d58913b1d6be83e948cc0bdf3d52b9df8ea`).
7. Tried the kit's official grader:
   `node cli/makefun.mjs grade-local --kit . --bot <entry> --driver process --worktree`
   verified the kit (29 files) and re-derived the dataset (1,440 bars from
   38,815 samples), then stopped with: "the process sandbox runs node22
   only (python3.13 runs only inside Docker)". Docker is not installed on
   this machine, so no official local grade was possible; the protocol
   drive in step 6 is the verification. The server will grade the Python
   bot in Docker at submission.

## Result

- Net PnL (dev): **+$29.18** — passes the dev gate (> $0) with margin.
- Trades: 8. Max drawdown: 1.92% — passes the guardrails.
- Determinism: verified, two runs byte-identical.

## Files in this entry

- `main.py`, `vendor/makefun_bars.py`, `README.md`, `LICENSE` (MIT),
  `DESIGN.md`, `BUILD_LOG.md`
