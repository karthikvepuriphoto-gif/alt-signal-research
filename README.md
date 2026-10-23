# alt-signal-research

**Backtest-only** research into unusual trading signals: El Niño/La Niña and weather, calendar and event anomalies, and social media (Reddit, X/Twitter). Nothing here places trades.
It runs alongside [`value-screen-backtest`](https://github.com/karthikvepuriphoto-gif/value-screen-backtest), which tests value-screen hypotheses (sector, size, election cycle, macro).

Last full run: 2026-10-23. Every number below comes from the scripts and data in this repo.

## Bottom line
* **283 hypotheses tested. 15 survive Benjamini–Hochberg correction (FDR 5%)** across all families together. The p-value histogram (`charts/pvalue_histogram.png`) has a real excess near zero, so not everything is noise. Most survivors are known calendar effects that have **decayed since publication**, or ENSO→commodity links that rest on only a handful of independent El Niño/La Niña *episodes* since 2000.
* **Most promising for further testing (none is ready to trade yet):**
  1. **ENSO → grains and fertilizer (short/underweight after El Niño becomes public).** After El Niño is declared (ONI ≥ 0.5, using only data available at the time), wheat fell 2.6%/month relative to other months (t = −4.1) and CF+MOS trailed SPY by 3.5%/month (t = −3.2). Both held up out-of-sample (2000+ / 2014+), stayed after controlling for each asset's own momentum and reversal, and got stronger for strong events (ONI ≥ 1.0). Weak points: the effect only exists **since 2000**, which is only about 6–7 El Niño episodes. Futures-based wheat (ZW=F) has t ≈ −1 to −1.2 by subperiod (t = −2.6 with controls). It also weakens if you wait an extra month or two. This is the opposite of the "El Niño raises commodity prices" headline (Cashin et al.; Brunner): the price spike happens *while* El Niño is building, and the tradeable signal is the reversal afterwards.
  2. **La Niña → energy (crude PPI, coal stocks, CL=F) up.** Crude PPI rose 2.0%/month more in La Niña months (t = 3.4, OOS t = 2.7). It is positive in all 4 subperiods since 1950 (t from 1.5 to 2.0 in each). 2013–2026 is heavily driven by 2021–22, when La Niña coincided with the energy shock, so there is confounding risk.
  3. **Reddit WallStreetBets attention spikes → fade, don't follow.** Buying names whose WSB comments spike 5× above their 20-day average loses about 0.9% the next day after 30 bp costs (t = −3.0, survives BH). The loss is larger out-of-sample (−1.7%/day, t = −4.2). Only about 5 years of data. Shorting meme names has borrow costs, squeeze risk and fees this doesn't model.
* **Calendar anomalies are real in the long CRSP history but mostly gone in SPY today.** Pre-FOMC drift and pre-holiday days are not significant after publication (OOS t = 1.0 and 1.5). Monday is null in SPY. Turn-of-month is the strongest of them (+6 bp/day post-1988, t = 2.2), but in SPY it's +0.4 bp (t = 0.1).
* **Things that did NOT work:** hurricane-season timing for insurers and homebuilders (0 of 18 survive), copying congressional trades after disclosure, S&P 500 inclusion reversal, options-expiration week, DST Mondays, moon phase (the intended null came out null, which is a good sanity check), Trump company tweets, and Musk→DOGE after the tweet day (+3.7% on the tweet day itself, t = 2.8, but **nothing once you can trade**).

## Ranked table (top 30 by p-value; the full table of 283 is in `results/ALL_HYPOTHESES_ranked.csv`)
Column notes: Effect is the full-sample effect. IS is the in-sample/pre-publication period and OOS the out-of-sample/post-publication period (the split date for each row is in the CSV). BH ✓ means q < 0.05 across all 283 tests. OOS ✓ means the OOS effect has the same sign as IS and p_OOS < 0.10.

| # | Family | Hypothesis | n | Effect (full) | Unit | t | BH q | IS effect | OOS effect (t) | BH ✓ | OOS ✓ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | B_Calendar | Monday vs other weekdays [CRSP VW mkt excess] | 4838 | -15.99 | bp/day diff | -8.71 | 0.000 | -24.56 | -5.84 (-2.0) | ✅ | ✅ |
| 2 | B_Calendar | Turn-of-month (day -1..+3) [CRSP VW mkt excess] | 4808 | +11.77 | bp/day diff | 7.07 | 0.000 | +15.14 | +6.27 (2.2) | ✅ | ✅ |
| 3 | B_Calendar | Pre-holiday day [CRSP VW mkt excess] | 895 | +22.36 | bp/day diff | 6.92 | 0.000 | +30.71 | +7.78 (1.5) | ✅ | — |
| 4 | A_ENSO | IMF wheat | ElNino(ONI>=0.5) vs other months | 107 | -2.59 | %/month diff | -4.10 | 0.003 | -2.48 | -2.69 (-2.9) | ✅ | ✅ |
| 5 | A_ENSO | FF:Coal-Mkt | LaNina(ONI<=-0.5) vs other months | 238 | +2.74 | %/month diff | 3.69 | 0.013 | +2.23 | +3.61 (2.1) | ✅ | ✅ |
| 6 | A_ENSO | IMF wheat | next1m ret ~ ONI | 416 | -1.23 | %/month per 1C ONI | -3.49 | 0.023 | -0.89 | -1.56 (-3.2) | ✅ | ✅ |
| 7 | A_ENSO | ETF EWW-SPY | next3m ret ~ ONI | 365 | -3.12 | %/month per 1C ONI | -3.44 | 0.024 | -2.10 | -3.61 (-3.0) | ✅ | ✅ |
| 8 | A_ENSO | PPI crude | LaNina(ONI<=-0.5) vs other months | 238 | +1.97 | %/month diff | 3.36 | 0.027 | +1.13 | +3.41 (2.7) | ✅ | ✅ |
| 9 | A_ENSO | Fert CF+MOS-SPY | ElNino(ONI>=0.5) vs other months | 100 | -3.52 | %/month diff | -3.22 | 0.038 | -2.56 | -4.19 (-3.3) | ✅ | ✅ |
| 10 | B_PEAD | PEAD short bottom-decile EPS surprise, hold 21d | 6070 | -0.53 | % CAR net vs SPY | -3.20 | 0.038 | -0.45 | -0.62 (-2.3) | ✅ | ✅ |
| 11 | A_ENSO | Fert CF+MOS-SPY | next1m ret ~ ONI | 405 | -1.74 | %/month per 1C ONI | -3.17 | 0.038 | -0.76 | -2.49 (-4.0) | ✅ | ✅ |
| 12 | A_ENSO | ETF EWW-SPY | next1m ret ~ ONI | 367 | -1.02 | %/month per 1C ONI | -3.16 | 0.038 | -0.78 | -1.04 (-2.3) | ✅ | ✅ |
| 13 | A_ENSO | IMF maize | LaNina(ONI<=-0.5) vs other months | 111 | +2.00 | %/month diff | 3.07 | 0.047 | +1.12 | +2.92 (3.1) | ✅ | ✅ |
| 14 | B_Calendar | Pre-FOMC/FOMC announcement day [CRSP VW mkt excess] | 254 | +22.71 | bp/day diff | 3.01 | 0.050 | +32.36 | +11.83 (1.0) | ✅ | — |
| 15 | C_Social | WSB comment spike >=5x 20d avg & >=100/day, all, hold 1d long (momentum) | 312 | -0.93 | % CAR net 30bp vs SPY | -3.01 | 0.050 | -0.28 | -1.70 (-4.2) | ✅ | ✅ |
| 16 | A_ENSO | IMF wheat | next3m ret ~ ONI | 414 | -2.80 | %/month per 1C ONI | -2.86 | 0.076 | -1.54 | -4.03 (-3.1) | — | ✅ |
| 17 | B_Calendar | Pre-FOMC/FOMC announcement day [SPY] | 254 | +21.03 | bp/day diff | 2.81 | 0.080 | +31.12 | +9.43 (0.9) | — | — |
| 18 | C_Social | Musk Dogecoin post: tweet-day DOGE-BTC AR (NOT tradeable) | 68 | +3.73 | % (net 20bp if tradeable) | 2.80 | 0.080 |  |  () | — | — |
| 19 | A_ENSO | FF:Steel-Mkt | LaNina(ONI<=-0.5) vs other months | 238 | +1.20 | %/month diff | 2.78 | 0.080 | +1.02 | +1.48 (1.6) | — | — |
| 20 | B_Calendar | Pre-FOMC/FOMC announcement day [IWM small caps] | 205 | +31.67 | bp/day diff | 2.68 | 0.103 | +52.70 | +16.40 (1.1) | — | — |
| 21 | A_ENSO | Fert CF+MOS-SPY | next3m ret ~ ONI | 403 | -4.01 | %/month per 1C ONI | -2.63 | 0.111 | -1.24 | -6.18 (-4.0) | — | ✅ |
| 22 | A_Hurricane | Fut NG=F | Aug-Oct peak vs rest | 80 | +5.80 | %/month diff | 2.63 | 0.111 | +5.28 | +6.32 (2.4) | — | ✅ |
| 23 | A_Hurricane | FF:BldMt-Mkt | Aug-Oct peak vs rest | 229 | -0.62 | %/month diff | -2.59 | 0.115 | -0.64 | -0.58 (-1.1) | — | — |
| 24 | A_ENSO | Fut ZC=F | next1m ret ~ ONI | 315 | -1.32 | %/month per 1C ONI | -2.59 | 0.115 | -1.53 | -1.09 (-1.6) | — | — |
| 25 | A_ENSO | IMF maize | next1m ret ~ ONI | 416 | -0.93 | %/month per 1C ONI | -2.57 | 0.116 | -0.72 | -1.12 (-2.1) | — | ✅ |
| 26 | B_PEAD | PEAD long top-decile EPS surprise, enter close day after reaction, hold 63d | 6007 | +2.12 | % CAR net vs SPY | 2.55 | 0.117 | +2.08 | +2.17 (1.6) | — | — |
| 27 | A_ENSO | FF:Oil-Mkt | next3m ret ~ ONI | 915 | -1.28 | %/month per 1C ONI | -2.53 | 0.118 | -0.33 | -3.05 (-2.8) | — | ✅ |
| 28 | A_ENSO | IMF maize | next3m ret ~ ONI | 414 | -2.30 | %/month per 1C ONI | -2.43 | 0.151 | -1.91 | -2.68 (-2.1) | — | ✅ |
| 29 | A_Hurricane | FF:Util-Mkt | Aug-Oct peak vs rest | 229 | +0.67 | %/month diff | 2.40 | 0.152 | +0.91 | +0.22 (0.4) | — | — |
| 30 | C_Social | WSB comment spike >=3x 20d avg & >=50/day, bullish, hold 5d long (momentum) | 314 | -1.20 | % CAR net 30bp vs SPY | -2.38 | 0.152 | -0.38 | -1.90 (-2.1) | — | ✅ |


### Hypotheses per family
| family      |   hyps |   p_lt_05 |   survive_BH |   expected_p<.05_by_chance |
|:------------|-------:|----------:|-------------:|---------------------------:|
| A_ENSO      |    184 |        32 |            9 |                        9.2 |
| A_Hurricane |     18 |         9 |            0 |                        0.9 |
| B_Calendar  |     22 |         6 |            4 |                        1.1 |
| B_Congress  |      6 |         0 |            0 |                        0.3 |
| B_Index     |      6 |         2 |            0 |                        0.3 |
| B_Insider   |      9 |         1 |            0 |                        0.4 |
| B_PEAD      |      4 |         3 |            1 |                        0.2 |
| C_Social    |     34 |         3 |            1 |                        1.7 |

## Method and rigor
* **No lookahead.** ONI (NOAA CPC, 1950–2026) for a 3-month season is used only from the **end of the month after the season ends**. CPC publishes in roughly the first 10 days of that month. Robustness runs with 1 or 2 extra months of lag are in `results/enso_robustness_specs.csv`. Insider trades are timed by Form-4 **filing** date, entering at the next close. Congressional trades use the PTR filing date, entering 2 trading days later. PEAD enters at the close *after* the reaction day, with surprise deciles from a trailing 365-day distribution. WSB spikes enter at the close of the trading day after the snapshot date.
* **Costs:** 10–20 bp per switch for monthly regimes (equities/commodities), 2–3 bp per round trip for index event days, 20 bp round trip for stock events, 30 bp for WSB names, 20 bp for DOGE.
* **Inference:** Newey–West HAC t-stats for time series and calendar-time portfolios for stock events (to handle overlapping events). Bootstrap p-values for the small tweet samples. **Benjamini–Hochberg over all 283 hypotheses jointly.** Robustness specs (lags, thresholds) are *not* counted as extra hypotheses and are reported separately.
* **IS/OOS:** calendar anomalies use the **original paper's publication year** as the split (McLean–Pontiff style). ENSO uses 1950–1999 / 2000–2026 (or the midpoint of shorter series). Stock events use 2011–2018 / 2019–2026, congress 2019–2022 / 2023–2026, and WSB 2021-04–2023-06 / 2023-07–2026-10.

## Branches
| Branch | Contents |
|---|---|
| `main` | This summary, the combined ranking (`combine.py`), charts, and the literature review (`LITERATURE.md`) |
| `enso-weather` | ENSO + hurricane backtests, robustness, subperiods and controls |
| `calendar-anomalies` | FOMC, turn-of-month, pre-holiday, OpEx, DST, moon, Monday, Halloween |
| `event-signals` | Insider Form-4 clusters, PEAD, S&P 500 additions/deletions, House congressional trades |
| `social-media` | WSB attention spikes (Tradestie daily top-50), Trump company tweets, Musk Dogecoin posts (X API) |

## Charts
`charts/all_hypotheses_top30.png`, `charts/pvalue_histogram.png`, `charts/oni_realtime.png`, `charts/enso_top_is_oos.png`, `charts/enso_regime_cumulative.png`, `charts/calendar_rolling.png`, `charts/insider_cluster3_cum.png`, `charts/musk_doge.png`

## Data sources and gaps
* NOAA CPC ONI (`oni.txt`). Ken French 49-industry and factor files (CRSP, through 2026-08). FRED PPI (corn, wheat, crude, from 1947) and IMF monthly commodity prices (from 1992). Yahoo Finance daily prices (front-month futures from 2000, country ETFs from 1996+). SEC Form 3/4/5 data sets (2011Q1–2026Q1, 500k open-market purchases). House Clerk PTRs 2019–2026 (3,800 PDFs parsed, 781 scanned/unparseable, 38,750 rows; parser from `day-trader-skill`). Fed FOMC calendars (255 meetings, 1994–2026). Tradestie WSB daily top-50 (2021-04 → 2026-10, about 1,750 usable days). Trump Twitter Archive (bpb27, 2016-11 → mid-2018). X API search for Musk "doge/dogecoin" posts (90 posts, 68 distinct days).
* **Gaps and caveats:**
  * The stock universe is current S&P 500/400 names (taken from the sibling repo), so it has **survivorship bias**. This probably explains why "short the PEAD losers" made money for the losers.
  * IMF/PPI commodity series are monthly *averages* and not investable. Futures confirmations are weaker, and yfinance continuous front-month contracts include roll jumps (the NG=F hurricane result especially).
  * Senate trades not included (behind a click-through). Pushshift/full Reddit history unavailable, so only top-50 snapshots. WSB tickers include some false positives (words like "AI" or "DD").
  * Google Trends, short interest, 13F "guru" following, spin-offs and sports sentiment were **not tested**, because there was no reliable free bulk history.
  * X search may miss deleted posts. The Trump archive covers only about 1.6 years of the presidency.
  * ENSO tests are many monthly observations but few independent episodes.

## Reproduce
```
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python fetch_prices.py; python fomc_dates.py; bash fetch_form4.sh; python build_insider.py; python fetch_ptr.py; python build_congress.py; python fetch_wsb.py; python fetch_earn.py
for a in "1 0.5" "2 0.5" "3 0.5" "1 1.0"; do python enso_backtest.py $a; done
python calendar_anomalies.py; python insider_test.py; python events_b.py; python congress_test.py; python trump_test.py; python musk_test.py; python wsb_test.py
python combine.py; python enso_robustness.py; python enso_subperiods.py; python charts.py; python make_readme.py
```
Research only, not investment advice.
