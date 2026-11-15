# Dip-Buy BTC Bot — btc-race-24h-20261115-0828

A bot that trades Coinbase Wrapped BTC (cbBTC) against USDC on 1-minute
bars, protocol `agent-fun/bars-replay/v1`. Long only, $1,000 paper money,
stdlib only, fully deterministic.

## Strategy

Buy the dip in two tranches, ride the rebound with a trailing stop:

- **Tranche 1:** flat and the close is ≥ 2.25% below the highest close of
  the last 60 bars → buy with half the cash.
- **Tranche 2:** holding one tranche and the close is ≥ 2.75% below that
  same rolling high → buy with the rest of the cash.
- **Exit:** sell everything when the close falls 0.75% below the highest
  close since entry (trailing stop), or when the position is worth 5%
  below its cost (stop-loss).
- Orders cap slippage at 100 bps past the close they were decided on.

All decisions are exact integer comparisons on the raw integer closes, so
two runs on the same data produce byte-identical orders.

## Files

- `main.py` — the bot (Python 3.13, stdlib only)
- `vendor/makefun_bars.py` — byte-identical copy of the kit's Python SDK shim
- `DESIGN.md` — strategy and local dev-grade result
- `BUILD_LOG.md` — how the entry was built and graded locally

## Local dev grade (kit's frozen dev window, 1,440 bars)

- Net PnL: **+$29.18** (final cash $1,029.18 on $1,000 start)
- Trades: **8** (4 round trips)
- Max drawdown: **1.92%**
- Determinism: two full protocol runs produce byte-identical reply streams

The dev gate needs net PnL > $0; this entry clears it with margin. The
official grade runs the same bot in the kit's Docker sandbox; the local
process driver runs Node only, so the local grade above was produced by
driving `main.py` through the protocol with the kit harness's own fill
math (fee 4 bps, slippage 2 bps, constant-product impact on bar depth),
which the offline parameter search replicated exactly.
