"""Index regime composite over the 50 perpetuals (written 2026-11-12; pre-registered before it was run).

NOT the IndexRegimeGraph strategy of dhruuvsharma/DaxAlgo-Terminal-Strategies. That one runs the Advanced Market Regime stack
on eight timeframes for Dow or S&P constituents; the judge has crypto perpetuals, daily. This is a crypto analogue of its
composite: each coin gets a trend score from six daily horizons, the scores are weighted by the coin's share of traded value
(the index weight stand-in), and the whole basket is held long, short or flat by the composite.

    score[coin]  = mean over h in (3, 7, 14, 30, 60, 90) of tanh( ln(close / close h days ago) / (sd of daily log returns over 90 days * sqrt(h)) )
    weight[coin] = its mean traded value over the last 30 days / the sum over coins
    composite    = sum of weight * score                       (between -1 and +1)
    state        long above +band, short below -band; back to flat when the composite is inside +-band/2
    holding      the basket at the weights, signed, sum of absolute weights 1; weights are set when the state changes
"""
from __future__ import annotations

import math

from strategy_lab.contract import CrossSectionStrategy

HORIZONS = (3, 7, 14, 30, 60, 90)


class IndexRegimeCompositeProxy(CrossSectionStrategy):
    name = "index_regime_composite_proxy"
    version = "1"

    def __init__(self, band: str = "0.25", **kw):
        super().__init__(band=band)
        self.band = float(band)
        self.closes = {}
        self.values = {}
        self.state = 0

    def on_day(self, day, close, value):
        for k, c in close.items():
            self.closes.setdefault(k, []).append(c)
            self.values.setdefault(k, []).append(value.get(k, 0.0))
        scores, wts = {}, {}
        for k in close:
            h = self.closes[k]
            if len(h) < 91:
                continue
            rets = [math.log(h[i] / h[i - 1]) for i in range(len(h) - 90, len(h))]
            mean = sum(rets) / 90
            sd = math.sqrt(sum((r - mean) ** 2 for r in rets) / 90) or 1e-9
            scores[k] = sum(math.tanh(math.log(h[-1] / h[-1 - n]) / (sd * math.sqrt(n))) for n in HORIZONS) / len(HORIZONS)
            v = self.values[k][-30:]
            wts[k] = sum(v) / len(v)
        total = sum(wts.values())
        if len(scores) < 20 or total <= 0:
            return None
        comp = sum(scores[k] * wts[k] / total for k in scores)
        old = self.state
        if comp > self.band:
            self.state = 1
        elif comp < -self.band:
            self.state = -1
        elif abs(comp) < self.band / 2:
            self.state = 0
        if self.state == old:
            return None
        return {k: self.state * wts[k] / total for k in scores} if self.state else {}
