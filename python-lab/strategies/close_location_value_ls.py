from collections import deque
from strategy_lab.contract import CrossSectionStrategy


class CloseLocationValueLS(CrossSectionStrategy):
    name = "close_location_value_ls"
    version = "1"

    def __init__(self, avg="20", rng="5", n="5", every="7", **kw):
        super().__init__(avg=avg, rng=rng, n=n, every=every, **kw)
        self.avg = int(avg)
        self.rng = int(rng)
        self.n = int(n)
        self.every = int(every)
        self.px = {}
        self.clv = {}
        self.days = 0

    def on_day(self, day, close, value):
        self.days += 1
        for k, c in close.items():
            p = self.px.setdefault(k, deque(maxlen=self.rng))
            p.append(c)
            if len(p) == self.rng:
                hi = max(p)
                lo = min(p)
                v = 0.5 if hi <= lo else (c - lo) / (hi - lo)
                self.clv.setdefault(k, deque(maxlen=self.avg)).append(v)
        if self.days % self.every:
            return None
        score = {}
        for k in close:
            d = self.clv.get(k)
            if d is not None and len(d) == self.avg:
                score[k] = sum(d) / len(d)
        m = min(self.n, len(score) // 2)
        if m < 1:
            return None
        order = sorted(score, key=lambda k: (-score[k], k))
        longs = order[:m]
        shorts = order[-m:]
        w = 1.0 / (2 * m)
        out = {k: w for k in longs}
        for k in shorts:
            out[k] = -w
        return out
