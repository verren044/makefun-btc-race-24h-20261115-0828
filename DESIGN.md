# DESIGN.md — btc-race-24h-20261115-0828

## Strategy in one line

Dip-buying mean reversion: buy cbBTC in two tranches on a 2.25–2.75% pullback
from the 60-bar high, exit on a 0.75% trailing stop or a 5% stop-loss.

## Why this shape

- The dev window is a falling market (BTC −4.00% over 24h, 67,216 → 64,524).
  Buy-and-hold loses ~$40; a bot must stay in cash through the grind and
  catch the rebounds. 1-minute return stdev is ~12 bps while a full-size
  round trip costs ~26 bps (4 bps fee + 2 bps slippage each way, plus
  ~15 bps of pool impact at the observed depth), so a trade needs a move
  well above 26 bps to pay. Intraday swings of 2–4% exist; the strategy
  only trades those.
- EMA-crossover and RSI/Bollinger baselines were grid-searched on the exact
  replay math and all lost money on this window (best EMA −$29.95, best
  RSI/BB −$22.81). Breakout momentum was marginal (+$4.88). Dip-buying won
  clearly, and the winning region is a plateau, not a knife-edge: for a
  60-bar lookback, drop thresholds 210–275 bps with a 75–100 bps trailing
  stop are all positive (+$6.84 to +$30.50).

## Parameters

| Parameter | Value | Meaning |
|---|---|---|
| `LOOKBACK` | 60 bars | rolling-high window (closes, current bar included) |
| `DROP1_BPS` | 225 | tranche 1: close 2.25% below rolling high, buy 50% of cash |
| `DROP2_BPS` | 275 | tranche 2: close 2.75% below rolling high, buy rest of cash |
| `TRAIL_BPS` | 75 | trailing stop: 0.75% below peak close since entry |
| `SL_BPS` | 500 | stop-loss: position worth 5% below cost |
| `MAX_SLIPPAGE_BPS` | 100 | order rejected rather than filled >1% past decision close |

## Local dev-grade result (kit's frozen dev window, 1,440 bars)

| Metric | Value |
|---|---|
| Net PnL | **+$29.18** (final cash $1,029.18) |
| Trades | 8 filled orders (4 round trips) |
| Max drawdown | 1.92% (guardrail: ≤ 25%) |
| Guardrail trades | ≥ 1: yes |
| Determinism | two full protocol runs: byte-identical reply streams (sha256 `f045cc64d0e0696768aeeb2ce4560d58913b1d6be83e948cc0bdf3d52b9df8ea`) |

Trade log (dev window): buy $1,000-equivalent in two tranches near the
deep dip around bar 995–1031 (~$62.3–63.0k), trailing stop exits the first
round trip at a small loss (−$12.63), the second tranche rides the rebound
to ~$64.7k (+$36.97). Two earlier small winning round trips (+$7.73,
+$7.66) complete the total.

## Method

The kit's harness source (`harness/sim/bars/engine.ts`) was replicated in
integer arithmetic (fee 4 bps, slippage 2 bps, constant-product impact
against each bar's open depth, max-slippage and decision checks, flatten
at the last close) and used to grid-search EMA-cross, RSI/Bollinger,
breakout, and dip families. The chosen parameters were then implemented
in `main.py` (integer comparisons only) and verified by driving the real
bot subprocess through the `agent-fun/bars-replay/v1` protocol over the
full dev dataset: the bot's result matches the offline simulation exactly
(+$29.18, 8 trades, 1.92% max DD).

## Caveats

- The dev window is one 24h sample; the race window is unseen. The
  strategy's edge is the plateau across drop 210–275 bps, not a single
  tuned point, and the trailing stop plus 5% stop-loss cap the loss per
  round trip, but a race window with no ≥2.25% pullback from a 60-bar high
  would produce few or zero trades (guardrail needs ≥1).
- The kit's `grade-local --driver process` runs Node bots only; a Python
  bot needs Docker, which is unavailable on this machine, so the official
  dev grade will be produced by the server at submission time.
