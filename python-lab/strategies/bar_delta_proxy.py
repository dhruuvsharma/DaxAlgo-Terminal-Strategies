"""Bar-delta proxy scalper, long or flat (written 2026-11-12; pre-registered before it was run).

NOT the CumulativeDelta strategy of dhruuvsharma/DaxAlgo-Terminal-Strategies. That one sums aggressor-side trade-tape volume
and gates on a spread in basis points; the judge's single-coin route sees only 1-minute open, high, low, close and volume, so
neither exists here. This is a proxy with the same shape, named for what it is: each bar's delta is estimated from where the
close sits inside the bar's range (close-location value) times the bar's volume.

    delta[t]  = volume * ((close - low) - (high - close)) / (high - low)      (0 for a flat bar)
    S[t]      = sum of the last `window` deltas
    theta[t]  = k * population sd of S over the last `sigma_n` bars            (the adaptive threshold)
    enter     S crosses above +theta, the last 3 deltas sum above 0, and the close is above its `ema_n`-bar average
    exit      S falls below 0, or `hold` bars have passed
"""
from __future__ import annotations

from collections import deque
from decimal import Decimal
from statistics import pstdev

from strategy_lab.contract import BarView, Target, TargetStrategy


class BarDeltaProxy(TargetStrategy):
    name = "bar_delta_proxy"
    version = "1"

    def __init__(self, window: int = 30, k: str = "1.5", sigma_n: int = 240, ema_n: int = 240, hold: int = 30, size: str = "0.1"):
        super().__init__(window=window, k=k, sigma_n=sigma_n, ema_n=ema_n, hold=hold, size=size)
        self.window, self.k, self.sigma_n, self.ema_n, self.hold = int(window), float(k), int(sigma_n), int(ema_n), int(hold)
        self.size = Decimal(size)
        self.deltas = deque(maxlen=self.window)
        self.sums = deque(maxlen=self.sigma_n)
        self.ema = None
        self.prev_s = None
        self.held = 0
        self.long = False

    def on_bar(self, bar: BarView) -> Target | None:
        rng = bar.high - bar.low
        d = bar.volume * ((bar.close - bar.low) - (bar.high - bar.close)) / rng if rng > 0 else 0.0
        self.deltas.append(d)
        a = 2.0 / (self.ema_n + 1)
        self.ema = bar.close if self.ema is None else self.ema + a * (bar.close - self.ema)
        if len(self.deltas) < self.window:
            return None
        s = sum(self.deltas)
        self.sums.append(s)
        prev, self.prev_s = self.prev_s, s
        if len(self.sums) < self.sigma_n // 2 or prev is None:
            return None
        if self.long:
            self.held += 1
            if s < 0 or self.held >= self.hold:
                self.long = False
                return Target(Decimal(0), f"delta proxy {s:,.0f} fell below 0 or {self.hold} bars passed")
            return None
        theta = self.k * pstdev(self.sums)
        last3 = list(self.deltas)[-3:]
        if prev <= theta < s and sum(last3) > 0 and bar.close > self.ema:
            self.long = True
            self.held = 0
            return Target(self.size, f"delta proxy {s:,.0f} crossed above {theta:,.0f}; last 3 bars bought; close above its {self.ema_n}-bar average")
        return None
