from strategy_lab.contract import CrossSectionStrategy
import statistics


class ReturnDispersionLS(CrossSectionStrategy):
    name = "return_dispersion_ls"
    version = "1"

    def __init__(self, window="30", n="5", **kw):
        super().__init__(window=window, n=n, **kw)
        self.w = int(window)
        self.n = int(n)
        self.hist = []

    def _weekday(self, day):
        y, m, d = int(day[0:4]), int(day[5:7]), int(day[8:10])
        t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
        if m < 3:
            y -= 1
        return (y + y // 4 - y // 100 + y // 400 + t[m - 1] + d) % 7  # 0=Sunday, 1=Monday

    def on_day(self, day, close, value):
        self.hist.append(dict(close))
        if len(self.hist) > self.w + 1:
            self.hist = self.hist[-(self.w + 1):]
        if self._weekday(day) != 1:
            return None
        if len(self.hist) < self.w + 1:
            return None
        score = {}
        for k in close:
            px = []
            ok = True
            for h in self.hist:
                p = h.get(k)
                if p is None or p <= 0:
                    ok = False
                    break
                px.append(p)
            if not ok:
                continue
            rets = [px[i] / px[i - 1] - 1 for i in range(1, len(px))]
            mabs = sum(abs(r) for r in rets) / len(rets)
            if mabs <= 0:
                continue
            score[k] = statistics.stdev(rets) / mabs
        if len(score) < 2 * self.n:
            return None
        order = sorted(score, key=lambda k: (score[k], k))
        longs = order[:self.n]
        shorts = order[-self.n:]
        wt = 1.0 / (2 * self.n)
        out = {}
        for k in longs:
            out[k] = wt
        for k in shorts:
            out[k] = -wt
        return out
