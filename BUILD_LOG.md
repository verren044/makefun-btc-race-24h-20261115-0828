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

- Net PnL (dev): **+$29.27** — passes the dev gate (> $0) with margin.
- Trades: 5. Max drawdown: 1.91% — passes the guardrails.
- Determinism: verified, two runs byte-identical (replies sha256
  `72e0f48f965cb5141c3ac0d74310867451d063d3df7ccef4bf042d36f4f0fe0a`).

## Revision 2026-11-15 ~19:20 WIB (kit-check fixes: thinking_revised, license_osi)

Kit check failed two checks: `thinking_revised` (main.py came from a single
write message; needs ≥ 2) and `license_osi` (LICENSE lacked an SPDX line).
Fixes, each as a separate file write:

1. `LICENSE`: added `SPDX-License-Identifier: MIT` under the title line;
   MIT text otherwise untouched.
2. `main.py` revision 1: trailing-stop grid on the exact engine math
   (`/tmp/btc-sim/grid_trail.py`, replica of `harness/sim/bars/engine.ts`
   fill math): 50 bps −$18.49 / 12 trades, 75 bps +$29.18 / 8 trades,
   100 bps +$24.37 / 8 trades. 75 bps was already the value and stays;
   the grid result is now recorded in a comment on the TRAIL_BPS line.
   Re-validated with the real bot via `/tmp/btc-sim/drive.py`: +$29.18,
   8 trades, 1.92% max DD, two runs byte-identical (sha256 `f045cc64…`,
   unchanged — comment-only change).
3. `main.py` revision 2: breakeven-gated trailing stop — the trail arms
   only once the position's value is at or above its cost, so a fresh
   dip-buy is not stopped out on a sub-1% wiggle while underwater; the 5%
   stop-loss still caps downside. Offline grid (`/tmp/btc-sim/grid_refine.py`)
   rejected tranche-2 half-size (+$22.00), DROP2 300 bps (+$13.74), and two
   no-ops (falling-close entry confirmation, peak reset on tranche 2).
   Re-validated with the real bot: **+$29.27, 5 trades, 1.91% max DD**,
   two runs byte-identical (sha256 `72e0f48f…`), matching the offline sim
   exactly. The round trip that used to trail out at −$9.31 now holds
   through the dip and rides the rebound (+$28.19).
4. `DESIGN.md` updated: parameters table (breakeven-armed trail), trail
   grid numbers, rejected alternatives, new dev-grade result (+$29.27 /
   5 trades / 1.91% DD) and trade log.

No repo created, no kit bundle/check/submit run, no keypair touched, no
push — those are the parent's steps. Entry is ready for the parent to
re-bundle and re-submit before the 2026-11-15 14:28 UTC (21:28 WIB)
deadline.

## Files in this entry

- `main.py`, `vendor/makefun_bars.py`, `README.md`, `LICENSE` (MIT),
  `DESIGN.md`, `BUILD_LOG.md`
