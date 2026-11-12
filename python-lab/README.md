# python-lab: strategies judged by the Hyperion validation lab

Independent Python versions of strategy ideas, each judged once by a private validation engine (costs included, a sealed holdout used once, every
try counted). Research code, **not trading advice**; nothing here places orders. They are not copies of the C# plugins under `archive/`
(`CumulativeDelta` and `IndexRegimeGraph` need trade-tape and constituent data the lab does not read, so the two proxies are named as proxies).
Code in this folder is AGPL-3.0 like the rest of the repository.

## Status
Of the strategies in `strategies/`, `bar_delta_proxy`, `index_regime_composite_proxy` and `weekly_resid_reversal_ls` **failed**; five cross-coin strategies
(`weekly_max_lottery_ls`, `gap_to_60d_high_weekly`, `close_location_value_ls`, `jump_share_ls_weekly`, `return_dispersion_ls`) got the judge's **Pass**
among many tries per family (about 5% pass by luck) and have no paper-trading record yet. A Pass is a hard-gate verdict, not a recommendation.

## The 18 strategies of the blog "퀀트가 돈을 버는 18가지 트레이딩 전략들" (Henry's Quant University, 2026-11-01), with what the lab can test
Summaries are paraphrased from the post's own table; references are the ones the post cites. Entries 5, 10 and 17 are only partly visible in the copy used.

| # | Strategy | One line | References | Testable in the lab |
|---|---|---|---|---|
| 1 | Momentum | buy what rose recently, sell what fell | Jegadeesh & Titman 1993 | yes |
| 2 | Mean reversion | bet that price returns to its long-run mean (or a spread between two names does) | Poterba & Summers 1988; Khandani & Lo 2007; Lehmann 1990; Lo & MacKinlay 1990; De Bondt & Thaler 1985 | yes |
| 3 | Statistical arbitrage | model how many names usually move together; bet that those far from the flow return; balance long and short so market direction matters less (market-neutral) | Avellaneda & Lee 2010; used at AQR, Renaissance, D. E. Shaw, Millennium | yes (cross-coin) |
| 4 | Pairs trading | find two names that usually move together; short the one that rose more vs. its mean, buy the lagging one; unwind when the gap closes | Gatev, Goetzmann & Rouwenhorst 2006; Do & Faff 2010; Rad, Low & Faff 2016 | yes |
| 5 | Trend following | buy rising markets, sell falling ones | not visible | yes |
| 6 | Market making | quote bid and ask together and earn the spread | Hendershott et al 2011; Menkveld 2013; Aquilina et al 2022 (Virtu: 1 losing day in 1,238 in its filing) | no: needs order book and queue |
| 7 | Event-driven | trade around dated events: mergers, earnings, index inclusion | Bennett, Stulz & Wang 2020; Bernard & Thomas 1989, 1990 | partly: only the FOMC calendar exists; no earnings or deals |
| 8 | Factor investing | long/short on characteristics long rewarded | Fama & French 2015; Asness, Moskowitz & Pedersen 2013; AQR, Robeco | yes (crypto: size, volatility, beta, liquidity) |
| 9 | Carry trade | borrow the low-rate asset, invest in the high-rate one | Menkhoff et al 2012; Brunnermeier, Nagel & Pedersen 2008 | yes (perpetual funding) |
| 10 | Volatility arbitrage | trade the gap between implied and expected volatility (text cut) | not visible | no: needs options data |
| 11 | Option strategies | sell options for premium, or buy as insurance (covered call, protective put) | Bondarenko 2016; Hewitt & EnnisKnupp 2012 | no: needs options data |
| 12 | Cross-sectional alpha | score every name daily or monthly; buy the high scores, sell the low | Kakushadze 2016, "101 Formulaic Alphas" | yes |
| 13 | Short-term reversal | names that spike or plunge on volume tend to partly revert within minutes to days | Nagel 2012; Heston, Korajczyk & Sadka 2010 | yes |
| 14 | Breakout trading | buy above the recent high, sell below the recent low | George & Hwang 2004; Zarattini, Barbon & Aziz | yes |
| 15 | Risk parity | spread equal risk, not equal money | Qian 2005; Bridgewater All Weather | yes (weights across coins) |
| 16 | Regime switching | judge or predict the market regime and cut or raise risk | none given (used by quant-macro funds) | yes as a gate |
| 17 | Machine-learning alpha | a computer finds return patterns in data (detail not visible) | not visible | partly: pure-Python sandbox, no ML libraries |
| 18 | Execution algorithms | split large orders to cut impact | Tóth 2011 | no: needs fills and book; not an alpha |
| 1 | Momentum | 32 | 30 Fail, 2 Inconclusive |
| 2 | Mean reversion | 6 | 6 Fail |
| 3 | Statistical arbitrage | 8 | 6 Fail, 2 Inconclusive |
| 4 | Pairs | 18 | 18 Fail |
| 5 | Trend following | 13 | 11 Fail, 2 Inconclusive |
| 8 | Factor investing | 68 | 3 Pass, 65 Fail |
| 9 | Carry | 34 | **9 Pass**, 5 Inconclusive, 20 Fail |
| 12 | Cross-sectional alpha | 180 | 4 Pass, 174 Fail, 2 Inconclusive |
| 13 | Short-term reversal | 24 | 24 Fail |
| 14 | Breakout | 5 | 1 Pass, 4 Fail |
| 15 | Risk parity | 4 | 4 Fail |
| 16 | Regime switching | 7 | 7 Fail |
| 17 | ML alpha | 1 | 1 Fail |

## Backtests (representative runs)
Simulated, after costs; cross-coin = daily, the 50 most traded perpetuals (test 2025, holdout 2026-01..10); single-coin = BTCUSDT bars.

| # | Blog strategy | Representative runs | Verdict | Test | Holdout |
|---|---|---|---|---|---|
| 1 | Momentum | cross-sectional 56-day / 90-day, skip 7, long 5 short 5 | Fail / Fail | Sharpe beats luck with probability 0.75 / 0.63 | -13.35% / -22.88% |
| 1 | Momentum | `btc_residual_momentum_weekly` (best test return of the family) | Fail | +205.7% | -33.1% |
| 2 | Mean reversion | `btc_1h_zscore_reversion` (BTCUSDT 1h) | Fail | -738.98 USDT | -185.49 USDT |
| 3 | Statistical arbitrage | `weekly_resid_reversal_ls` (residual reversion; M2 conformance passes) | Fail | -48.20% | +21.02% |
| 4 | Pairs trading | `avax_sol_pairs_zscore` | Fail | +31.6% | +3.3% |
| 4 | Pairs trading | BNB/ETH, LINK/ETH, ETH/SOL (window 30) | Fail x3 | -32.9%, -12.9%, -21.8% | +5.5%, n/a, n/a |
| 5 | Trend following | `xs_ema_slope_weekly_ls` | Fail | +163.5% | -29.1% |
| 5 | Trend following | `btc_4h_dual_return_trend` (BTCUSDT 4h) | Fail | +738.44 USDT | -971.85 USDT |
| 8 | Factor investing | `weekly_max_lottery_ls` (lottery / MAX factor, long-short) | **Pass** | +115.4% | +12.2% |
| 8 | Factor investing | `close_location_value_ls`, `lottery_coins_short` | **Pass**, **Pass** | see ledger | see ledger |
| 9 | Carry trade | `funding_carry_btc` (short perp, long spot) | **Pass** | +4.50% | +2.11% |
| 9 | Carry trade | `funding_carry_eth`, `funding_carry_doge_xrp` | **Pass**, **Pass** | +4.15%, +2.48% | +0.97%, +1.02% |
| 9 | Carry trade | funding carry SOL, BNB, XRP | Fail, Fail, Inconclusive | -0.37% (SOL) | n/a |
| 12 | Cross-sectional alpha | `return_consistency_ls` (best test return) | Fail | +294.0% | -12.2% |
| 12 | Cross-sectional alpha | `jump_share_ls_weekly`, `return_dispersion_ls`, `weekly_max_lottery_ls` | **Pass** x3 | see ledger | see ledger |
| 13 | Short-term reversal | `weekly_reversal_14d_ls` | Fail | +35.6% | +26.6% |
| 14 | Breakout trading | `gap_to_60d_high_weekly` (George & Hwang 2004 idea) | **Pass** | +118.79% | +1.21% |
| 14 | Breakout trading | `breakout_count_ls_weekly` | Fail | +79.6% | -38.3% |
| 15 | Risk parity | `eq_weight_btc_eth_sol_monthly`, `weekly_inverse_vol_top10` | Fail x2 | -14.4%, -33.1% | -19.0%, -20.4% |
| 16 | Regime switching | `regime_composite_ls` | Fail | +84.8% | -31.0% |
| 17 | Machine-learning alpha | `weekly_ridge_xs_longshort` | Fail | +12.1% | -8.7% |
| - | DaxAlgo CumulativeDelta idea (bar-delta proxy) | script run and Hyperion chat | Fail, Fail | -11,551 / -11,590 USDT | -4,145 / -4,158 USDT |
| - | DaxAlgo IndexRegimeGraph idea (crypto composite) | script run and Hyperion chat | Fail, Fail | -12.68% / -12.67% | -13.43% / -9.99% |

## Reading it
- **Carry is the one blog strategy with a repeatable, modest Pass** (BTC, ETH, DOGE/XRP: +2.5% to +4.5% a year with positive holdouts), which fits a funding premium; its pass rate (9 of 34 tries) is far above the luck level.
- **Several families pass or nearly pass on the factor side** (the lottery/MAX factor, the distance-to-high breakout), but with 68 and 180 tries per family a few passes are expected by chance. Their paper books have 0 paper days so far: the paper-versus-backtest comparison is due around 2026-12-02.
- **Many cross-coin runs show a large test return and a negative holdout** (momentum, trend, cross-sectional alpha, regime): the signature of fitting one year.
- **Not testable here:** market making (6), event-driven (7, only the FOMC calendar exists), volatility arbitrage (10), options (11), execution algorithms (18), and the machine-learning entry beyond a pure-Python ridge (17).
- Judge power (`m5_planted_null_report.md`): a strong planted edge is usually found, a weak one often missed, and nothing is accepted in a world with no signal.
