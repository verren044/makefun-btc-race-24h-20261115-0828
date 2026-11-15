"""Dip-buying BTC bot for make.fun btc-race-24h-20261115-0828.

Strategy: buy the dip in two tranches, ride the rebound with a trailing stop.
Long only, one symbol (CBBTC), one open position, stdlib only, fully
deterministic (integer arithmetic only, no clock, no network, no files).

Rules, decided on each 1-minute bar's close (fills land at the next bar's
open, so every decision is made on closes already seen):
  - Entry tranche 1: flat and the close is at least DROP1_BPS below the
    highest close of the last LOOKBACK bars (including this bar): buy with
    half the cash.
  - Entry tranche 2: holding one tranche and the close is at least
    DROP2_BPS below that same rolling high: buy with the rest of the cash.
  - Exit: sell the whole position when the close falls TRAIL_BPS below the
    highest close since entry (trailing stop, armed only once the position
    is at or above breakeven), or when the position is worth SL_BPS below
    its cost (stop-loss).

All comparisons are exact integer comparisons on the raw integer closes
(price_scale 5), so two runs on the same data produce byte-identical
orders. The rolling high is the max of the last LOOKBACK+1 closes; a bar
with no CBBTC bar (a gap) adds nothing and triggers no order.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
LOOKBACK = 60          # bars in the rolling-high window
DROP1_BPS = 225        # first tranche: close 2.25% below the rolling high
DROP2_BPS = 275        # second tranche: close 2.75% below the rolling high
TRAIL_BPS = 75         # trailing stop: 0.75% below the peak close since entry
# Trail grid on the exact engine math, dev window: 50 bps -> -$18.49 (12
# trades), 75 bps -> +$29.18 (8 trades), 100 bps -> +$24.37 (8 trades).
# 75 bps is the winner; 50 bps whipsaws out of every rebound.
SL_BPS = 500           # stop-loss: position worth 5% below its cost
MAX_SLIPPAGE_BPS = 100  # 1% past the close the order was decided on
MIN_NOTIONAL = 1_000_000  # 1 USDC, in quote units


class DipBot:
    def __init__(self):
        self.closes = []       # CBBTC closes, ints, in bar order
        self.peak = None       # highest close since entry, int or None
        self.added = False     # second tranche already bought

    def on_batch(self, state, batch):
        fresh = False
        for bar in batch["bars"]:
            if bar["symbol"] == SYMBOL:
                self.closes.append(int(bar["c"]))
                fresh = True
        if state.warming_up or not fresh:
            return []
        if len(self.closes) < LOOKBACK + 1:
            return []

        close = self.closes[-1]
        high = max(self.closes[-(LOOKBACK + 1):])
        held = state.positions.get(SYMBOL)

        if held is not None and held.qty > 0:
            if self.peak is None or close > self.peak:
                self.peak = close
            # Trailing stop protects gains only: it arms once the position is
            # at or above breakeven, so a fresh dip-buy is not stopped out on
            # a sub-1% wiggle while still underwater (the 5% stop-loss below
            # still caps the downside). Dev: +$29.27 / 5 trades vs +$29.18 / 8
            # without the gate — the round trip that trailed out at -$9.31
            # instead holds through the dip and rides the same rebound.
            in_profit = state.value(SYMBOL, held.qty) >= held.cost
            if in_profit and close * 10000 <= self.peak * (10000 - TRAIL_BPS):
                self.peak = None
                self.added = False
                return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            if state.value(SYMBOL, held.qty) * 10000 <= held.cost * (10000 - SL_BPS):
                self.peak = None
                self.added = False
                return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            if not self.added and close * 10000 <= high * (10000 - DROP2_BPS):
                self.added = True
                room = state.equity - state.value(SYMBOL, held.qty)
                amount = state.cash if state.cash < room else room
                if amount >= MIN_NOTIONAL:
                    return [{"side": "buy", "symbol": SYMBOL,
                             "notional_quote_units": amount,
                             "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            return []

        self.peak = None
        self.added = False
        if close * 10000 <= high * (10000 - DROP1_BPS):
            self.peak = close
            amount = state.cash // 2
            if amount >= MIN_NOTIONAL:
                return [{"side": "buy", "symbol": SYMBOL,
                         "notional_quote_units": amount,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []


makefun_bars.run(DipBot().on_batch)
