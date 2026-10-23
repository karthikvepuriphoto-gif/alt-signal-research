# alt-signal-research

**Backtest-only** research into unusual trading signals: El Niño/La Niña and weather, calendar and event anomalies, and social media (Reddit, X/Twitter). Nothing here places trades.
It runs alongside [`value-screen-backtest`](https://github.com/karthikvepuriphoto-gif/value-screen-backtest), which tests value-screen hypotheses (sector, size, election cycle, macro).

Last full run: 2026-10-23. Every number below comes from the scripts and data in this repo.

## Bottom line
* **{{N}} hypotheses tested. {{NBH}} survive Benjamini–Hochberg correction (FDR 5%)** across all families together. The p-value histogram (`charts/pvalue_histogram.png`) has a real excess near zero, so not everything is noise. Most survivors are known calendar effects that have **decayed since publication**, or ENSO→commodity links that rest on only a handful of independent El Niño/La Niña *episodes* since 2000.
* **Most promising for further testing (none is ready to trade yet):**
  1. **ENSO → grains and fertilizer (short/underweight after El Niño becomes public).** After El Niño is declared (ONI ≥ 0.5, using only data available at the time), wheat fell 2.6%/month relative to other months (t = −4.1) and CF+MOS trailed SPY by 3.5%/month (t = −3.2). Both held up out-of-sample (2000+ / 2014+), stayed after controlling for each asset's own momentum and reversal, and got stronger for strong events (ONI ≥ 1.0). Weak points: the effect only exists **since 2000**, which is only about 6–7 El Niño episodes. Futures-based wheat (ZW=F) has t ≈ −1 to −1.2 by subperiod (t = −2.6 with controls). It also weakens if you wait an extra month or two. This is the opposite of the "El Niño raises commodity prices" headline (Cashin et al.; Brunner): the price spike happens *while* El Niño is building, and the tradeable signal is the reversal afterwards.
  2. **La Niña → energy (crude PPI, coal stocks, CL=F) up.** Crude PPI rose 2.0%/month more in La Niña months (t = 3.4, OOS t = 2.7). It is positive in all 4 subperiods since 1950 (t from 1.5 to 2.0 in each). 2013–2026 is heavily driven by 2021–22, when La Niña coincided with the energy shock, so there is confounding risk.
  3. **Reddit WallStreetBets attention spikes → fade, don't follow.** Buying names whose WSB comments spike 5× above their 20-day average loses about 0.9% the next day after 30 bp costs (t = −3.0, survives BH). The loss is larger out-of-sample (−1.7%/day, t = −4.2). Only about 5 years of data. Shorting meme names has borrow costs, squeeze risk and fees this doesn't model.
* **Calendar anomalies are real in the long CRSP history but mostly gone in SPY today.** Pre-FOMC drift and pre-holiday days are not significant after publication (OOS t = 1.0 and 1.5). Monday is null in SPY. Turn-of-month is the strongest of them (+6 bp/day post-1988, t = 2.2), but in SPY it's +0.4 bp (t = 0.1).
* **Things that did NOT work:** hurricane-season timing for insurers and homebuilders (0 of 18 survive), copying congressional trades after disclosure, S&P 500 inclusion reversal, options-expiration week, DST Mondays, moon phase (the intended null came out null, which is a good sanity check), Trump company tweets, and Musk→DOGE after the tweet day (+3.7% on the tweet day itself, t = 2.8, but **nothing once you can trade**).

## Ranked table (top 30 by p-value; the full table of {{N}} is in `results/ALL_HYPOTHESES_ranked.csv`)
Column notes: Effect is the full-sample effect. IS is the in-sample/pre-publication period and OOS the out-of-sample/post-publication period (the split date for each row is in the CSV). BH ✓ means q < 0.05 across all {{N}} tests. OOS ✓ means the OOS effect has the same sign as IS and p_OOS < 0.10.

{{TABLE}}

### Hypotheses per family
{{FAM}}

## Method and rigor
* **No lookahead.** ONI (NOAA CPC, 1950–2026) for a 3-month season is used only from the **end of the month after the season ends**. CPC publishes in roughly the first 10 days of that month. Robustness runs with 1 or 2 extra months of lag are in `results/enso_robustness_specs.csv`. Insider trades are timed by Form-4 **filing** date, entering at the next close. Congressional trades use the PTR filing date, entering 2 trading days later. PEAD enters at the close *after* the reaction day, with surprise deciles from a trailing 365-day distribution. WSB spikes enter at the close of the trading day after the snapshot date.
* **Costs:** 10–20 bp per switch for monthly regimes (equities/commodities), 2–3 bp per round trip for index event days, 20 bp round trip for stock events, 30 bp for WSB names, 20 bp for DOGE.
* **Inference:** Newey–West HAC t-stats for time series and calendar-time portfolios for stock events (to handle overlapping events). Bootstrap p-values for the small tweet samples. **Benjamini–Hochberg over all {{N}} hypotheses jointly.** Robustness specs (lags, thresholds) are *not* counted as extra hypotheses and are reported separately.
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
