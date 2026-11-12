from strategy_lab.contract import CrossSectionStrategy


def _weekday(day):
    y, m, d = int(day[0:4]), int(day[5:7]), int(day[8:10])
    if m <= 2:
        y -= 1
    era = y // 400
    yoe = y - era * 400
    mp = m - 3 if m > 2 else m + 9
    doy = (153 * mp + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    days = era * 146097 + doe - 719468
    return (days + 3) % 7  # Monday = 0


class WeeklyMaxLottery(CrossSectionStrategy):
    name = "weekly_max_lottery_ls"
    version = "1"

    def __init__(self, lookback="30", n="5", min_obs="25", **kw):
        super().__init__(lookback=lookback, n=n, min_obs=min_obs, **kw)
        self.lb = int(lookback)
        self.n = int(n)
        self.min_obs = int(min_obs)
        self.hist = []

    def on_day(self, day, close, value):
        self.hist.append(dict(close))
        if len(self.hist) > self.lb + 1:
            self.hist = self.hist[-(self.lb + 1):]
        if _weekday(day) != 6:  # Sunday close -> positions held from Monday 00:00 UTC
            return None
        if len(self.hist) < self.min_obs + 1:
            return None
        score = {}
        for k in close:
            best = None
            cnt = 0
            for i in range(1, len(self.hist)):
                a = self.hist[i - 1].get(k)
                b = self.hist[i].get(k)
                if a is None or b is None or a <= 0:
                    continue
                r = b / a - 1.0
                cnt += 1
                if best is None or r > best:
                    best = r
            if cnt >= self.min_obs and best is not None:
                score[k] = best
        if len(score) < 2 * self.n:
            return None
        ranked = sorted(score, key=lambda k: (score[k], k))
        longs = ranked[:self.n]
        shorts = ranked[-self.n:]
        w = 1.0 / (2 * self.n)
        out = {}
        for k in longs:
            out[k] = w
        for k in shorts:
            out[k] = -w
        return out
