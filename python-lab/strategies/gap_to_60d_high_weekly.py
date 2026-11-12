from strategy_lab.contract import CrossSectionStrategy


def _weekday(day):
    y, m, d = int(day[0:4]), int(day[5:7]), int(day[8:10])
    y -= m <= 2
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    mp = (m + 9) % 12
    doy = (153 * mp + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    days = era * 146097 + doe - 719468
    return (days + 3) % 7


class GapTo60dHigh(CrossSectionStrategy):
    name = "gap_to_60d_high_weekly"
    version = "1"

    def __init__(self, window="60", n="5", **kw):
        super().__init__(window=window, n=n, **kw)
        self.w = int(window)
        self.n = int(n)
        self.hist = {}

    def on_day(self, day, close, value):
        for k, v in close.items():
            h = self.hist.setdefault(k, [])
            h.append(v)
            if len(h) > self.w:
                del h[0]
        if _weekday(day) != 0:
            return None
        score = {}
        for k, v in close.items():
            h = self.hist.get(k, [])
            if len(h) >= self.w and v > 0:
                hi = max(h)
                if hi > 0:
                    score[k] = v / hi
        if len(score) < 2 * self.n:
            return None
        ranked = sorted(score, key=lambda k: (-score[k], k))
        longs = ranked[:self.n]
        shorts = ranked[-self.n:]
        wt = 1.0 / (2 * self.n)
        out = {}
        for k in longs:
            out[k] = wt
        for k in shorts:
            out[k] = -wt
        return out
