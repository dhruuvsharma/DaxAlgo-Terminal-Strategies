from strategy_lab.contract import CrossSectionStrategy
import math


class JumpShareLS(CrossSectionStrategy):
    name = "jump_share_ls_weekly"
    version = "1"

    def __init__(self, window="30", k="3.0", n="5", **kw):
        super().__init__(window=window, k=k, n=n, **kw)
        self.w = int(window)
        self.k = float(k)
        self.n = int(n)
        self.hist = []

    @staticmethod
    def _weekday(day):
        y, m, d = int(day[0:4]), int(day[5:7]), int(day[8:10])
        t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
        if m < 3:
            y -= 1
        return (y + y // 4 - y // 100 + y // 400 + t[m - 1] + d) % 7  # 0=Sunday, 1=Monday

    def _score(self, coin):
        px = [h.get(coin) for h in self.hist[-(self.w + 1):]]
        if len(px) < self.w + 1 or any(p is None or p <= 0 for p in px):
            return None
        r = [math.log(px[i + 1] / px[i]) for i in range(self.w)]
        mu = sum(r) / len(r)
        dev2 = [(x - mu) ** 2 for x in r]
        tot = sum(dev2)
        if tot <= 0:
            return None
        sd = math.sqrt(tot / (len(r) - 1))
        thr = (self.k * sd) ** 2
        jump = sum(v for v in dev2 if v > thr)
        return (jump / tot, tot)

    def on_day(self, day, close, value):
        self.hist.append(dict(close))
        if len(self.hist) > self.w + 1:
            self.hist = self.hist[-(self.w + 1):]
        if self._weekday(day) != 1:
            return None
        sc = {}
        for c in close:
            s = self._score(c)
            if s is not None:
                sc[c] = s
        if len(sc) < 2 * self.n:
            return None
        order = sorted(sc, key=lambda c: (sc[c][0], sc[c][1], c))
        longs = order[:self.n]
        shorts = order[-self.n:]
        wt = 1.0 / (2 * self.n)
        out = {}
        for c in longs:
            out[c] = wt
        for c in shorts:
            out[c] = -wt
        return out
