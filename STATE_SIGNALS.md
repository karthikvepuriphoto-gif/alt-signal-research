# Phase 2 — State-level signals (branch `state-signals`)
Backtest only, no trading. All hypotheses were preregistered in [PREREGISTRATION.md](PREREGISTRATION.md) and committed before any test ran. BH correction is applied jointly over **310 hypotheses**: the 283 from Phase 1 plus 27 new ones. Code is in `state_tests.py` (main tests) and `state_robust.py` (exploratory robustness), with the data fetch in `fetch_state_data.py`. The chart is `charts/state_signals.png`.

## Headline
- **2 of 27** Phase 2 tests survive BH (q<0.05): DR8 and LB2. Both also hold OOS with the same sign. **However, both go in the OPPOSITE direction to the preregistered prediction**, so they count as failed predictions and newly found anomalies, not confirmations:
  - **DR8.** Stocks headquartered in states where drought *worsened* last month beat stocks in states where it eased, by 0.38%/month (t −4.5 for the preregistered L−S). OOS (2019+) the gap is 0.33%/month (t −2.5). The result holds after dropping CA, TX and NY. A caveat: the HQ-state mapping clusters stocks, and many states show ΔD2+=0 with ties broken at random. I have no ex-ante mechanism for this, so treat it with caution.
  - **LB2.** Stocks in states with rising initial claims *under*-perform (0.26%/month, t −3.0, OOS t −2.5). This contradicts the countercyclical-premium story in Korniotis-Kumar and is closer to a slow-diffusion/momentum effect in local economic news.
- **Near misses** (q<0.25, preregistered direction correct):
  - EN2: La Niña → energy firms HQ'd in TX/OK/ND/LA/CO +4.1%/month vs SPY (t 2.4, q 0.15). Almost all of it comes from OOS (+6.9%, t 3.0); IS was +0.2%. It largely overlaps the Phase 1 crude-in-La-Niña result.
  - DR6: West drought → hydro utilities −0.44%/month per 1sd (t −2.0, q 0.24).
  - ND4: hurricane declarations → homebuilders +4.3% over 60 days (t 2.1, n=48, IS-driven).
- **PO1** (Kim-Pantzalis-Park political alignment) goes in the opposite direction: aligned states −0.33%/month (t −2.7, q 0.088). It holds after dropping CA/TX/NY and after industry-demeaning (t −2.5).
- **Clear nulls:**
  - Corn Belt drought → DE/AGCO, ADM/BG, rails, fertilizer (all |t|<1.7 full-sample)
  - USAspending ≥$1bn/≥$5bn awards (t 0.1 / −1.0)
  - FEMA declarations → local banks and utilities
  - CA fire declarations → PCG/EIX
  - hurricanes → P&C insurers
  - state coincident index (LB1)
  - geographic lead-lag (LB3, t −0.3)
  - Medicaid and cannabis ballot events (n=5–6, underpowered)
  - EN1 physical check: La Niña → Southern Plains drought rise has the right sign but t 0.9

## Ranked table (Phase 2 rows; rank among all 310)
|   rank_of_310 | hyp                                                                                            | pred   |    n |   effect | unit                                                |      t |     p |   q_BH |   eff_is |   eff_oos |   t_oos | oos_confirms   | dir_ok   | small_sample   |
|--------------:|:-----------------------------------------------------------------------------------------------|:-------|-----:|---------:|:----------------------------------------------------|-------:|------:|-------:|---------:|----------:|--------:|:---------------|:---------|:---------------|
|             4 | DR8 HQ-state ΔD2+: long low-Δdrought-state minus high tercile (universe)                       | +      |  189 |   -0.381 | % per month L-S net of 10bp/side                    | -4.505 | 0     |  0.001 |   -0.432 |    -0.329 |  -2.488 | True           | False    | False          |
|            15 | LB2 State initial-claims YoY (4wk avg, lag 2w): long high-claims-growth minus low terciles     | +      |  189 |   -0.26  | % per month L-S net of 10bp/side                    | -3.016 | 0.003 |  0.048 |   -0.231 |    -0.289 |  -2.471 | True           | False    | False          |
|            22 | PO1 Aligned-with-President's-party HQ states minus non-aligned, eq-wt                          | +      |  166 |   -0.333 | % per month L-S net of 10bp/side                    | -2.735 | 0.006 |  0.088 |   -0.216 |    -0.422 |  -2.507 | True           | False    | False          |
|            31 | EN2 La Niña -> energy firms HQ TX/OK/ND/LA/CO (n=21) excess ret                                | +      |  189 |    4.055 | % next-month excess, La Niña minus other            |  2.44  | 0.015 |  0.145 |    0.246 |     6.947 |   2.982 | True           | True     | False          |
|            52 | ND4 Hurricane DR in FL/TX/LA/NC/SC -> homebuilders                                             | +      |   48 |    4.309 | % CAR [+1,+60] net of 20bp vs SPY                   |  2.145 | 0.037 |  0.221 |    7.17  |     2.266 |   0.771 | False          | True     | False          |
|            58 | DR6 West ΔD2+ -> hydro-exposed utilities IDA/AVA/POR/NWE/PCG/EIX                               | −      |  320 |   -0.437 | % next-month excess ret vs SPY per 1sd signal       | -2.005 | 0.045 |  0.24  |   -0.483 |    -0.421 |  -1.704 | True           | True     | False          |
|            78 | EN3 La Niña -> PNW hydro utilities IDA/AVA/POR                                                 | +      |  321 |    1.014 | % next-month excess, La Niña minus other            |  1.701 | 0.089 |  0.354 |    0.081 |     2.407 |   2.908 | True           | True     | False          |
|            81 | EN5 Corn Belt drought × El Niño interaction -> ag equipment                                    | −      |  162 |    3.414 | % interaction coef per 1sd                          |  1.673 | 0.094 |  0.361 |    2.423 |     2.922 |   1.402 | False          | False    | False          |
|            88 | DR4 Corn Belt ΔD2+ (Apr-Sep) -> fertilizer CF/MOS/NTR                                          | −      |  162 |    1.412 | % next-month excess ret vs SPY per 1sd signal       |  1.608 | 0.108 |  0.379 |    1.12  |     3.159 |   4.152 | True           | False    | False          |
|            94 | LB1 State coincident-index 3m growth (lag 2m): long weak-state minus strong-state terciles     | +      |  188 |   -0.171 | % per month L-S net of 10bp/side                    | -1.524 | 0.127 |  0.42  |   -0.257 |    -0.083 |  -0.438 | False          | False    | False          |
|            95 | PO4 Medicaid expansion ballot approvals -> Medicaid insurers CNC/MOH                           | +      |    5 |   -3.541 | % CAR [+1,+5] net of 20bp vs SPY                    | -1.896 | 0.131 |  0.427 |   -1.212 |    -5.094 |  -1.795 | False          | False    | True           |
|            98 | DR7 CA ΔD2+ -> CA water utilities CWT/HTO(SJW)/AWR                                             | −      |  320 |    0.305 | % next-month excess ret vs SPY per 1sd signal       |  1.478 | 0.14  |  0.44  |    0.288 |     0.253 |   1.508 | False          | False    | False          |
|           127 | ND1 FEMA major-disaster declaration -> utilities HQ in declared state                          | −      | 1157 |   -0.381 | % CAR [+1,+20] net of 20bp vs SPY (calendar-time t) | -1.164 | 0.244 |  0.596 |    0.022 |    -0.827 |  -2.222 | False          | True     | False          |
|           134 | EN4 El Niño -> farm-state HQ banks                                                             | −      |  189 |   -0.872 | % next-month excess, El Niño minus other            | -1.108 | 0.268 |  0.616 |   -0.514 |    -0.973 |  -0.934 | False          | True     | False          |
|           139 | ND5 CA fire DR/FM declarations -> PCG/EIX                                                      | −      |  216 |   -0.297 | % CAR [+1,+5] net of 20bp vs SPY                    | -1.071 | 0.285 |  0.636 |   -0.355 |    -0.22  |  -0.394 | False          | True     | False          |
|           144 | FS2 USAspending prime award ≥$5bn -> recipient                                                 | +      |   63 |   -0.343 | % CAR [+1,+5] net of 20bp vs SPY (calendar-time t)  | -1.033 | 0.302 |  0.647 |   -0.113 |    -0.743 |  -0.647 | False          | False    | False          |
|           147 | PO2 Recreational cannabis ballot election (wins +, 2024 all-fail −) -> cannabis basket         | +      |    6 |    9.779 | % CAR [+1,+5] net of 20bp vs SPY                    |  1.08  | 0.33  |  0.685 |    8.169 |    10.584 |   1.427 | False          | True     | True           |
|           155 | DR3 Corn Belt ΔD2+ (Apr-Sep) -> rails UNP/CSX/NSC                                              | −      |  162 |   -0.388 | % next-month excess ret vs SPY per 1sd signal       | -0.937 | 0.349 |  0.698 |   -0.25  |    -1.233 |  -0.624 | False          | True     | False          |
|           162 | EN1 La Niña (lag1) -> next-month ΔD2+ Southern Plains TX/OK/KS/NM (physical first stage)       | +      |  321 |    2.594 | pp change in % area D2+                             |  0.899 | 0.369 |  0.706 |    3.25  |     1.609 |   0.51  | False          | True     | False          |
|           163 | ND3 Hurricane DR in FL/TX/LA/NC/SC -> P&C insurers                                             | −      |   48 |    0.345 | % CAR [+1,+5] net of 20bp vs SPY                    |  0.895 | 0.375 |  0.711 |    0.479 |     0.249 |   0.568 | False          | False    | False          |
|           204 | DR2 Corn Belt ΔD2+ (Apr-Sep) -> grain merchandisers ADM/BG                                     | −      |  162 |    0.318 | % next-month excess ret vs SPY per 1sd signal       |  0.629 | 0.529 |  0.803 |   -0.036 |     2.444 |   3.098 | False          | False    | False          |
|           224 | DR5 Plains ΔD2+ -> farm-state HQ banks (n=1)                                                   | −      |  189 |    0.172 | % next-month excess ret vs SPY per 1sd signal       |  0.523 | 0.601 |  0.832 |   -0.325 |     0.803 |   1.785 | False          | False    | False          |
|           250 | LB3 Same-HQ-state peer return last month (own-ret residualized): long top minus bottom tercile | +      |  189 |   -0.036 | % per month L-S net of 10bp/side                    | -0.338 | 0.735 |  0.912 |   -0.112 |     0.041 |   0.259 | False          | False    | False          |
|           259 | PO3 Medicaid expansion ballot approvals -> hospitals HCA/UHS/THC/CYH                           | +      |    5 |   -0.726 | % CAR [+1,+5] net of 20bp vs SPY                    | -0.3   | 0.779 |  0.933 |   -2.331 |     0.344 |   0.085 | False          | False    | True           |
|           287 | FS1 USAspending prime award ≥$1bn (base obligation date) -> recipient                          | +      |  351 |   -0.102 | % CAR [+1,+5] net of 20bp vs SPY (calendar-time t)  |  0.126 | 0.899 |  0.971 |   -0.002 |    -0.2   |   0.421 | False          | False    | False          |
|           298 | DR1 Corn Belt ΔD2+ (Apr-Sep) -> ag equipment DE/AGCO/LNN/TITN                                  | −      |  162 |    0.05  | % next-month excess ret vs SPY per 1sd signal       |  0.072 | 0.943 |  0.981 |   -0.228 |     1.719 |   2.347 | False          | False    | False          |
|           299 | ND2 FEMA major-disaster declaration -> banks HQ in declared state                              | −      |  792 |    0.05  | % CAR [+1,+20] net of 20bp vs SPY (calendar-time t) | -0.058 | 0.954 |  0.989 |   -0.267 |     0.322 |   0.09  | False          | False    | False          |

dir_ok = effect sign matches the preregistered sign. oos_confirms = same sign IS/OOS and p_oos<0.10.

## Case studies (n=1, excluded from BH)
| id   | desc                                                                                  | value                                         |
|:-----|:--------------------------------------------------------------------------------------|:----------------------------------------------|
| LB4  | Own-state peer beta controlling for SPY (Pirinsky-Wang comovement), monthly 2011-2026 | median 0.653, mean 0.735, share>0 0.92, n=814 |
| PO5  | PO5 CA AB1228 $20 fast-food wage signed 2023-09-28, restaurants, [+1,+5] CAR vs SPY   | -0.31%                                        |
| PO6  | PO6 Murphy v NCAA 2018-05-14, gaming, [+1,+1] CAR vs SPY                              | 0.82%                                         |
| ND6  | ND6 Texas freeze 2021-02-12..+10d, TX power/gas, [+1,+10] CAR vs SPY                  | -6.63%                                        |

## Exploratory robustness (not preregistered)
| test   | dropped_states                   |   mean_monthly |       t |
|:-------|:---------------------------------|---------------:|--------:|
| DR8    | none                             |        -0.0038 | -4.5054 |
| LB2    | none                             |        -0.0026 | -3.0164 |
| PO1    | none                             |        -0.0033 | -2.7097 |
| DR8    | CA                               |        -0.0038 | -5.079  |
| LB2    | CA                               |        -0.0019 | -2.7778 |
| PO1    | CA                               |        -0.0023 | -2.5081 |
| DR8    | CA,TX                            |        -0.0033 | -5.9387 |
| LB2    | CA,TX                            |        -0.0017 | -2.6539 |
| PO1    | CA,TX                            |        -0.002  | -3.0335 |
| DR8    | CA,TX,NY                         |        -0.0029 | -4.3272 |
| LB2    | CA,TX,NY                         |        -0.0017 | -2.4626 |
| PO1    | CA,TX,NY                         |        -0.0022 | -3.415  |
| PO1    | industry-neutral (SIC2 demeaned) |        -0.0014 | -2.5436 |

## Data and method notes
- **US Drought Monitor:** state statistics API, categorical % area, weekly 2000-01 to 2026-10, all 50 states + DC. D2+ = D2+D3+D4; each map is treated as known 2 days after its valid date.
- **Philly Fed state coincident indexes:** FRED `{ST}PHCI`, lagged 2 months. These are the revised vintage, so there is some look-ahead from revisions; ALFRED vintages were not used. State initial claims: FRED `{ST}ICLAIMS`.
- **FEMA:** OpenFEMA DisasterDeclarationsSummaries v2, 50,889 rows; 1,644 major (DR) disasters since 2000; 48 hurricane event dates; 217 CA fire declaration dates.
- **USAspending:** 958 prime contracts ≥$1bn (FY2009–26) mapped by recipient-name regex to 352 listed-parent events. *Award Amount is the current cumulative value* (a size lookahead), and the base obligation date may precede the public DoD announcement.
- **HQ mapping:** EDGAR submissions for 881/904 universe names. This is the current address, not point-in-time.

## Data gaps
- Small farm-state banks are absent from the S&P 500/400 universe, so DR5/EN4 are effectively USB only.
- No point-in-time HQ or revenue-by-state data (10-K segment geography not parsed).
- Coval-Moskowitz needs 13F holdings, which were not pulled.
- Governor/legislature party changes, state tax changes and state minimum-wage schedules were not assembled, so only the presidential-alignment test was run.
- IRA/CHIPS grants have no clean announcement dates.
- Sports-betting state launches were not tested.
- Coincident-index real-time vintages (ALFRED) were not used.
- The universe is survivorship-biased (current constituents).

## Suggested next hypotheses
1. Replicate DR8/LB2 with point-in-time HQ (Compustat/EDGAR historical addresses) and CRSP small caps, and test whether they are a local-news momentum effect (Parsons et al. at the city level).
2. EN2 with energy *futures* hedged out, to see whether the effect goes beyond crude beta.
3. Hydro utilities vs NOAA Columbia River runoff forecasts (released before the water year).
4. Rebuild PO1 with Kim-Pantzalis-Park's exact state political-alignment index (governor + legislature + presidential), run it over 1990+ with CRSP data, and look at the 2017+ reversal.
5. DoD daily contract announcements (defense.gov, 5pm ET) instead of USAspending dates.
