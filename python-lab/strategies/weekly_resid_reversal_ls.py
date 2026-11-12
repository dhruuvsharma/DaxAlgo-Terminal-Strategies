from strategy_lab.contract import CrossSectionStrategy


def _days(day):
    y, m, d = int(day[0:4]), int(day[5:7]), int(day[8:10])
    if m <= 2:
        y -= 1
    era = y // 400
    yoe = y - era * 400
    mp = m - 3 if m > 2 else m + 9
    doy = (153 * mp + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


class WeeklyResidReversal(CrossSectionStrategy):
    name = "weekly_resid_reversal_ls"
    version = "1"

    def __init__(self, window="60", sumdays="5", n="5", **kw):
        super().__init__(window=window, sumdays=sumdays, n=n, **kw)
        self.win = int(window)
        self.sd = int(sumdays)
        self.n = int(n)
        self.hist = []

    def on_day(self, day, close, value):
        self.hist.append(dict(close))
        if len(self.hist) > self.win + 2:
            self.hist = self.hist[-(self.win + 2):]
        if (_days(day) + 3) % 7 != 0:
            return None
        if len(self.hist) < self.win + 1:
            return None
        h = self.hist[-(self.win + 1):]
        coins = [c for c in close if all((c in x and x[c] > 0) for x in h)]
        if len(coins) < 2 * self.n + 5:
            return None
        rets = {c: [h[i][c] / h[i - 1][c] - 1.0 for i in range(1, len(h))] for c in coins}
        T = self.win
        mkt = [sum(rets[c][t] for c in coins) / len(coins) for t in range(T)]
        mm = sum(mkt) / T
        vm = sum((x - mm) ** 2 for x in mkt)
        if vm <= 0:
            return None
        score = {}
        for c in coins:
            r = rets[c]
            mr = sum(r) / T
            cov = sum((mkt[t] - mm) * (r[t] - mr) for t in range(T))
            b = cov / vm
            a = mr - b * mm
            score[c] = sum(r[t] - a - b * mkt[t] for t in range(T - self.sd, T))
        order = sorted(coins, key=lambda k: (score[k], k))
        longs = order[:self.n]
        shorts = order[-self.n:]
        w = {}
        for c in longs:
            w[c] = 0.1
        for c in shorts:
            w[c] = -0.1
        return w
