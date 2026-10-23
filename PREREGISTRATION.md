# Phase 2 pre-registration: state-level signals (branch `state-signals`)

I wrote and committed this file **before** I ran any Phase 2 return test. The git commit timestamp is the proof. I may also report extra analyses, but every one is labelled "exploratory (not preregistered)". All preregistered tests go into one Benjamini-Hochberg family together with the **283 Phase 1 hypotheses**.

**General rules (all tests)**
- Backtest only. No trading.
- **State mapping.** Each company maps to a state by its SEC EDGAR business address (`data.sec.gov/submissions`, `addresses.business.stateOrCountry`). This is the current address, not point-in-time, which is a known limitation. Where a company's revenue or operating exposure is known (for example a regulated utility's service territory or a CA water utility), I use that exposure instead, and the hypothesis says so.
- **Universe.** Current S&P 500/400 constituents from `eq_adj.parquet` (2011–2026), plus named tickers from yfinance (longest history available, as far back as 2000). This universe is survivorship-biased.
- **No lookahead.**
  - USDM maps (valid Tuesday, released Thursday) are used from the following trading day; monthly signals use the last map published in month t.
  - The Philly Fed state coincident index is lagged 2 months (released about 4–5 weeks after the reference month, then revised).
  - State initial claims are lagged 2 weeks.
  - FEMA declarations count from the next trading day after `declarationDate`.
  - Election events start at the next session close after election day.
- **Costs.** 10 bp per side on monthly long-short rebalances (turnover-weighted). 20 bp round trip per event in event studies.
- **IS/OOS.** For monthly tests with 2000+ data, IS is 2000–2015 and OOS is 2016–2026. For 2011+ data, IS is 2011–2018 and OOS is 2019–2026.
- **Statistics.** Newey-West (6 lags monthly) t-stats and calendar-time portfolio t-stats. A test is a "small sample" if it has fewer than 20 events or fewer than 36 signal months.

## 1. Drought (US Drought Monitor, state % area in D2+ "severe or worse", weekly since 2000)
The signal is the change in D2+ % area over the month, expressed as a z-score. The tested quantity is the next-month return relative to SPY, regressed on the signal (sign = predicted sign of the coefficient).

| id | mechanism (literature) | drought region | stocks | pred. sign | horizon |
|---|---|---|---|---|---|
| DR1 | Drought cuts yields and farm income, so equipment demand falls (farm income drives capex; USDA ERS) | Corn Belt avg (IA, IL, IN, NE, MN), Apr–Sep months only | DE, AGCO, LNN, TITN eq-wt | − | 1 m |
| DR2 | Lower crop volumes mean lower origination/crush volume for grain merchandisers | Corn Belt, Apr–Sep | ADM, BG | − | 1 m |
| DR3 | Fewer grain carloads (AAR grain carloads track harvest) | Corn Belt, Apr–Sep | UNP, CSX, NSC | − | 1 m |
| DR4 | Fertilizer application and nutrient uptake fall in drought, and the next-season nitrogen outlook weakens | Corn Belt, Apr–Sep | CF, MOS, NTR | − | 1 m |
| DR5 | Farm-loan stress at ag-heavy banks (Kansas City Fed ag credit surveys) | Plains avg (IA, NE, KS, SD, ND, MN) | banks (SIC 6020-6029) HQ in those states | − | 1 m |
| DR6 | Low hydro output forces costly replacement power purchases (Gleick 2016 on the CA drought hydropower cost; EIA) | West avg (WA, OR, ID, CA, MT) | IDA, AVA, POR, NWE, PCG, EIX | − | 1 m |
| DR7 | Conservation mandates cut sales volumes (CA 2015 25% mandate) | CA | CWT, SJW, AWR | − | 1 m |
| DR8 | Local demand shock to firms in the drought state | each stock's HQ state | all universe stocks; cross-sectional long low-Δdrought-state minus high-Δdrought-state terciles | + (L−S) | 1 m |

## 2. State politics
| id | mechanism (literature) | events | stocks | pred. | horizon |
|---|---|---|---|---|---|
| PO1 | Political alignment: firms in states aligned with the President's party outperform (Kim, Pantzalis & Park 2012, JFE "Political geography and stock returns") | Aligned = the state voted for the sitting President in the most recent presidential election (maps: 2012 for 2013–16, 2016 for 2017–20, 2020 for 2021–24, 2024 for 2025–26) | universe; equal-weight aligned minus non-aligned | + | monthly |
| PO2 | Recreational cannabis ballot wins expand addressable markets (event studies of cannabis stocks around elections) | Election days with ≥1 recreational legalization win: 2016, 2018, 2020, 2022, 2023 (2024 all failed, sign −) | CGC, TLRY, ACB, CRON (+MSOS when available) eq-wt vs SPY | + | [+1,+5] d |
| PO3 | Medicaid expansion cuts uncompensated care for hospitals and grows Medicaid-managed-care enrollment (Dranove, Garthwaite & Ody 2016; Kaestner et al.) | ME 2017-11-07, ID/NE/UT 2018-11-06, OK 2020-06-30, MO 2020-08-04, SD 2022-11-08 (ballot approvals) | hospitals HCA, UHS, THC, CYH | + | [+1,+5] d |
| PO4 | Same mechanism, insurers | same events | CNC, MOH | + | [+1,+5] d |
| PO5 | Minimum-wage cost shock for restaurants (Aaronson 2001 price pass-through; Card-Krueger) | CA AB1228 $20 fast-food wage signing 2023-09-28 | CMG, MCD, YUM, JACK, WING, SBUX | − | [0,+5] d, **case study n=1, excluded from BH** |
| PO6 | Sports-betting legalization (Murphy v. NCAA, 2018-05-14) | 1 event | PENN, CZR, MGM, BYD, CHDN | + | [0,+1] d, **case study, excluded from BH** |

## 3. Federal spending (USAspending.gov)
| id | mechanism | events | stocks | pred. | horizon |
|---|---|---|---|---|---|
| FS1 | Large contract awards are cash-flow news (McGowan & Vendrzyk 2002; event studies of DoD contract announcements) | USAspending prime awards ≥ $1bn (base and all options), action date as event date, mapped to listed parents by recipient name | recipient stock vs SPY | + | [+1,+5] d |
| FS2 | Same, but scaled by size: the award is material when it is ≥ 1% of market cap (approximated as award ≥ 3% of trailing revenue is not available, so I use awards ≥ $5bn) | subset of FS1 | same | + | [+1,+5] d |

IRA/CHIPS award-level state grants have no clean investable event dates. These are reported as a data gap unless verified announcement dates are found.

## 4. Local bias / state business cycles
| id | mechanism (literature) | signal | stocks | pred. | horizon |
|---|---|---|---|---|---|
| LB1 | Local risk sharing is imperfect, so expected returns of local stocks are countercyclical in the state economy (Korniotis & Kumar 2013 JF) | 3-month growth of the Philly Fed state coincident index (lag 2 m) | long the bottom-tercile-growth HQ-state stocks minus the top tercile | + | 1 m |
| LB2 | Same mechanism, using labour-market weakness | YoY % change in the 4-week average of state initial claims (lag 2 w) | long the high-claims-growth-state terciles minus low | + | 1 m |
| LB3 | Geographic lead-lag: information diffuses slowly across firms in the same location (Parsons, Sabbatucci & Titman 2020 RFS); local comovement (Pirinsky & Wang 2006 JF) | last-month return of same-HQ-state peers (excluding own stock), with own last-month return as a control | long the top tercile of peer-return stocks minus the bottom | + | 1 m |
| LB4 | Pirinsky-Wang comovement (descriptive, not a trading test) | own-state vs other-state portfolio beta | all | own-state β > 0 | **descriptive, excluded from BH** |

## 5. Natural disasters (FEMA declarations since 2000)
| id | mechanism | events | stocks | pred. | horizon |
|---|---|---|---|---|---|
| ND1 | Storm restoration costs and regulatory lag (utility event studies) | first DR (major disaster) declaration per disaster number | utilities (SIC 4900-4949) HQ in the declared state | − | [+1,+20] d |
| ND2 | Local loan losses and deposit flows (Cortés & Strahan 2017 on banks after disasters) | same | banks (SIC 6020-6029) HQ in the state | − | [+1,+20] d |
| ND3 | P&C catastrophe losses, plus a hardening-market offset | Hurricane DR in FL/TX/LA/NC/SC | P&C insurers (TRV, ALL, CB, PGR, HIG, CINF, WRB, AIG) | − | [+1,+5] d |
| ND4 | Rebuilding demand | same hurricane events | homebuilders (DHI, LEN, PHM, NVR, TOL, KBH) | + | [+1,+60] d |
| ND5 | Utility wildfire liability (PG&E 2019 bankruptcy; inverse condemnation) | CA DR or FM declarations with incidentType Fire | PCG, EIX | − | [+1,+5] d |
| ND6 | Texas Feb-2021 freeze (ERCOT) | 2021-02-15 | VST, NRG, CNP, ATO, AEP | − | **case study, excluded from BH** |

## 6. Own hypotheses building on Phase 1 (ENSO survivors)
| id | mechanism | signal | stocks | pred. | horizon |
|---|---|---|---|---|---|
| EN1 | La Niña dries the southern US (NOAA CPC teleconnections). This is a first-stage physical check, not a return test | ONI ≤ −0.5 (lag 1) | Southern Plains (TX, OK, KS, NM) D2+ % next-month change | + | 1 m |
| EN2 | La Niña raised crude in Phase 1, so energy-state firms should benefit | ONI ≤ −0.5 (lag 1) months vs others | energy firms (SIC 1311, 1381, 1389, 2911) HQ in TX/OK/ND/LA/CO, eq-wt minus SPY | + | 1 m |
| EN3 | La Niña makes the Pacific Northwest wet, giving better hydro output | ONI ≤ −0.5 months | IDA, AVA, POR minus SPY | + | 1 m |
| EN4 | El Niño hurt fertilizer in Phase 1, and El Niño brings wetter Corn Belt/US conditions | ONI ≥ 0.5 months | farm-state banks (DR5 set) minus SPY | − | 1 m |
| EN5 | Drought × ENSO interaction: Corn Belt drought shocks matter more when ONI ≥ 0.5 (global grain glut) | DR1 signal × El Niño dummy | DR1 basket | − (interaction) | 1 m |
