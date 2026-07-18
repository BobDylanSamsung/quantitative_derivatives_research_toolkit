# Market Calibration and Implied-Volatility Analysis of SPY Options

## Testing the Constant-Volatility Assumption Using Real Option-Chain Data

---

## 1. Executive summary

This study applies a European-option pricing toolkit to a fixed snapshot of SPY option-chain data. Earlier work in the project showed that Black–Scholes–Merton, Cox–Ross–Rubinstein and Monte Carlo pricing agree when they are evaluated under the same assumptions. The purpose here is different: to test whether those assumptions, especially constant volatility, can explain real option prices across strikes and maturities.

The dataset contains 892 SPY call and put quotes collected through Yahoo Finance on 18 July 2026 at approximately 06:06 UTC, with SPY recorded at $\$743.289978$. Three expirations were analysed: 14 August 2026, 16 October 2026 and 15 January 2027, corresponding to 27, 90 and 181 days to expiry. Quotes were represented by bid–ask midpoints and filtered for valid two-sided markets, moderate moneyness, acceptable spreads and minimum open interest. The final sample contained 378 contracts, or 42.4% of the raw data.

All 378 retained quotes calibrated successfully using a bounded Brent root solver with theoretical price-bound checks. This confirms that the numerical inversion was robust on the selected dataset. It does not show that Black–Scholes–Merton is a complete market model; implied volatility is defined to make the model reproduce each observed price.

Calculated implied volatilities broadly matched Yahoo Finance's values. Mean calculated IV was 0.185832 versus 0.189335 for Yahoo, with a median absolute difference of 0.010519 and RMSE of 0.023741. The residuals were not random, however. Calculated call IVs were generally lower than Yahoo's, calculated put IVs were generally higher, and the separation widened at longer maturities.

The main result is the shape of the implied-volatility surface. All three expirations showed a clear downside skew. Near the forward, implied volatility was around 15–17%, while the shortest-dated downside IV approached 40%. The skew became flatter as maturity increased, showing that volatility varied with both strike and time to expiry. A single constant volatility could not reproduce the full SPY option-price cross-section.

Put–call parity was used as a secondary consistency check. Across 135 matched pairs, the overall median absolute error was $\$0.607573$, with the longest maturity showing the largest median deviation. These differences should not be treated automatically as arbitrage because the analysis uses midpoints, European parity for American-style options, simplified carry assumptions and potentially asynchronous quotes.

---

## 2. Research questions

This report addresses five questions:

1. Can the implied-volatility solver reliably calibrate real SPY option quotes?
2. How closely do the calculated implied volatilities agree with Yahoo Finance's values?
3. Can one constant volatility explain prices across strikes?
4. How does the implied-volatility skew change with maturity?
5. What do put–call parity deviations reveal about the data and modelling assumptions?

---

## 3. Model and methodology

### 3.1 Black–Scholes–Merton with dividends

The analysis uses the dividend-adjusted European Black–Scholes–Merton model. For spot $S_0$, strike $K$, maturity $T$, continuously compounded risk-free rate $r$, dividend yield $q$ and volatility $\sigma$,

$$
C
=
S_0 e^{-qT}N(d_1)
-
K e^{-rT}N(d_2),
$$

$$
P
=
K e^{-rT}N(-d_2)
-
S_0 e^{-qT}N(-d_1),
$$

where

$$
d_1
=
\frac{
\log(S_0/K)
+
\left(r-q+\frac{1}{2}\sigma^2\right)T
}{
\sigma\sqrt{T}
},
\qquad
d_2=d_1-\sigma\sqrt{T}.
$$

The model assumes European exercise and constant $r$, $q$ and $\sigma$. In this study it is used as a common pricing and calibration framework, not as a claim that SPY options satisfy those assumptions exactly.

Each market price is represented by the bid–ask midpoint:

$$
V_{\text{mid}}
=
\frac{V_{\text{bid}}+V_{\text{ask}}}{2}.
$$

Maturity follows an ACT/365 convention:

$$
T
=
\frac{\text{calendar days to expiry}}{365}.
$$

The analysis assumes

$$
r=4.0\%,
\qquad
q=1.2\%.
$$

### 3.2 Implied-volatility calibration

Implied volatility is the value $\sigma_{\text{impl}}$ satisfying

$$
V_{\text{BSM}}
\left(
S_0,K,r,q,T,\sigma_{\text{impl}}
\right)
=
V_{\text{market}}.
$$

Because this equation has no closed-form inverse for $\sigma$, the solver uses Brent's method over a bounded volatility interval. Before root-finding, each quote is checked against the European no-arbitrage bounds

$$
\max\left(
0,
S_0e^{-qT}-Ke^{-rT}
\right)
\leq C
\leq
S_0e^{-qT},
$$

and

$$
\max\left(
0,
Ke^{-rT}-S_0e^{-qT}
\right)
\leq P
\leq
Ke^{-rT}.
$$

The solver returns the recovered volatility, convergence status, iteration count and any failure reason. This makes it possible to distinguish numerical failure from invalid pricing inputs.

### 3.3 Forward moneyness and smile construction

The estimated forward price is

$$
F_0(T)
=
S_0e^{(r-q)T},
$$

and log-forward moneyness is

$$
k
=
\log\left(
\frac{K}{F_0(T)}
\right).
$$

Thus $k<0$ indicates a strike below the forward, $k=0$ is approximately at-the-money forward, and $k>0$ indicates a strike above the forward. Forward moneyness improves comparisons across maturities by accounting for the assumed cost of carry.

The main volatility-smile figure uses an out-of-the-money composite:

- OTM puts when $K\leq F_0(T)$;
- OTM calls when $K\geq F_0(T)$.

This avoids relying heavily on deep in-the-money quotes, where small price errors can produce large implied-volatility changes.

### 3.4 Put–call parity

For European options with continuous dividend yield,

$$
C-P
=
S_0e^{-qT}
-
Ke^{-rT}.
$$

For each matched call–put pair, the parity error is

$$
\varepsilon_{\text{parity}}
=
(C_{\text{mid}}-P_{\text{mid}})
-
\left(
S_0e^{-qT}-Ke^{-rT}
\right).
$$

Parity is used as a diagnostic of internal consistency, quote quality and carry assumptions rather than as a direct trading signal.

---

## 4. Data and filtering

### 4.1 Market snapshot

The analysis uses a fixed SPY option-chain snapshot obtained through `yfinance`.

| Field | Value |
|---|---:|
| Underlying | SPY |
| Collection time | 18 July 2026, approximately 06:06 UTC |
| Recorded spot price | $\$743.289978$ |
| Raw option quotes | 892 |
| Expirations analysed | 3 |

| Expiration | Days to expiry | Raw contracts |
|---|---:|---:|
| 14 August 2026 | 27 | 257 |
| 16 October 2026 | 90 | 224 |
| 15 January 2027 | 181 | 411 |

Using a fixed snapshot keeps the analysis reproducible as market prices and available contracts change.

### 4.2 Filtering

Contracts were required to have:

- bid greater than zero;
- ask greater than bid;
- 14–365 days to expiry;
- strike between 80% and 120% of spot;
- relative bid–ask spread no greater than 30%;
- open interest of at least 10 contracts.

These filters reduce the effect of stale, one-sided, very far-from-the-money and illiquid quotes. They do not remove all market-data noise.

| Stage | Quotes retained |
|---|---:|
| Raw prepared quotes | 892 |
| Valid two-sided market | 853 |
| 14–365 days to expiry | 853 |
| 80–120% spot moneyness | 459 |
| Liquidity filters | 378 |

The final retention rate was

$$
\frac{378}{892}
\approx
42.4\%.
$$

The median relative bid–ask spread among retained quotes was 1.3396%.

| Expiration | Calls | Puts | Total |
|---|---:|---:|---:|
| 14 August 2026 | 68 | 105 | 173 |
| 16 October 2026 | 57 | 42 | 99 |
| 15 January 2027 | 60 | 46 | 106 |
| **Total** | **185** | **193** | **378** |

---

## 5. Calibration validation

### 5.1 Solver convergence

All filtered quotes calibrated successfully:

| Metric | Result |
|---|---:|
| Quotes submitted | 378 |
| Successful calibrations | 378 |
| Failed calibrations | 0 |
| Success rate | 100% |

This result shows that the retained prices satisfied the solver conditions and produced bracketed roots. It is evidence of numerical robustness on this dataset, not evidence that one Black–Scholes volatility describes the market.

### 5.2 Comparison with Yahoo Finance

| Metric | Result |
|---|---:|
| Mean calculated IV | 0.185832 |
| Mean Yahoo IV | 0.189335 |
| Mean difference | -0.003504 |
| Median difference | -0.000985 |
| Median absolute difference | 0.010519 |
| RMSE | 0.023741 |
| Minimum difference | -0.083215 |
| Maximum difference | 0.061786 |

The two methods produced similar overall levels. The median absolute difference of 0.010519 is about 1.05 volatility points, while the larger RMSE reflects several more substantial discrepancies.

![[Pasted image 20260718172044.png]]

*Figure 1. Calculated European-model implied volatility against Yahoo Finance's supplied implied volatility. The dashed 45-degree line shows exact agreement. The broad alignment confirms similar overall levels, while the visible branches indicate systematic differences.*

The residuals separate by option type and maturity:

| Expiration | Option type | Quotes | Mean difference | Median absolute difference |
|---|---|---:|---:|---:|
| 14 August 2026 | Call | 68 | -0.008228 | 0.004065 |
| 14 August 2026 | Put | 105 | 0.007820 | 0.008758 |
| 16 October 2026 | Call | 57 | -0.027412 | 0.014834 |
| 16 October 2026 | Put | 42 | 0.014853 | 0.012247 |
| 15 January 2027 | Call | 60 | -0.029554 | 0.025278 |
| 15 January 2027 | Put | 46 | 0.024475 | 0.019723 |

Calculated call IVs were generally below Yahoo's estimates, while calculated put IVs were generally above them. The gap widened with maturity.

![[Pasted image 20260718172130.png]]

*Figure 2. Calculated IV minus Yahoo IV against log-forward moneyness, separated by option type. The persistent call and put branches suggest a methodological difference rather than random numerical error.*

Possible explanations include differences in:

- American versus European exercise treatment;
- dividend assumptions;
- interest-rate assumptions;
- price inputs;
- quote and spot timestamps;
- vendor filtering or calibration methodology.

The experiment does not establish which explanation dominates, and it does not show that either estimate is more correct.

---

## 6. Implied-volatility smile results

![[Pasted image 20260718172219.png]]

*Figure 3. OTM SPY implied-volatility smiles plotted against log-forward moneyness for the 27-, 90- and 181-day expirations. OTM puts are used below the forward and OTM calls above it. The dashed vertical line marks $k=0$.*

The OTM composite smile is the clearest result of the study. If one constant volatility explained the option chain, each expiration would be approximately flat. Instead, implied volatility changes materially with both strike and maturity.

All three expirations show a pronounced downside skew. As log-forward moneyness becomes more negative, implied volatility rises. Near the forward, IV is approximately 15–17%. At the lowest retained strikes, the 27-day implied volatility approaches 40%, compared with roughly 30% for the 90-day expiration and 27–28% for the 181-day expiration.

The skew is therefore strongest at the shortest maturity and becomes flatter as maturity increases. The right side of each smile falls to a local minimum before rising slightly at higher strikes. The shortest-dated curve has the most pronounced curvature, reaching a minimum near 11%.

These results imply that one volatility parameter cannot simultaneously fit downside puts, near-forward options and higher-strike calls. Even assigning one volatility to each maturity would still miss the cross-sectional variation across strikes. The market-implied object is better represented as a surface,

$$
\sigma_{\text{impl}}=\sigma_{\text{impl}}(K,T),
$$

rather than a single scalar.

The downside skew indicates that downside option exposure carries a higher implied-volatility premium than near-forward or upside exposure. The study does not identify one cause, but the pattern may reflect a combination of downside-protection demand, jump risk, non-normal return expectations and risk.

The stronger short-dated skew shows greater strike sensitivity over the shortest horizon in this snapshot. It should not be interpreted as a direct forecast that short-dated realised volatility will be higher. Implied volatility is a price-based model output and may include compensation for risks outside constant-volatility diffusion dynamics.

The important distinction is between numerical accuracy and model adequacy. The analytical, lattice and Monte Carlo methods can agree under shared Black–Scholes assumptions, while those assumptions remain too restrictive for real market data. Black–Scholes–Merton is still useful as a quoting and calibration framework, but constant volatility does not explain the full SPY option surface.

---

## 7. Put–call parity diagnostic

The analysis matched 135 call–put pairs. The overall median absolute parity error was

$$
\$0.607573.
$$

| Expiration | Matched pairs | Median absolute error | Maximum absolute error |
|---|---:|---:|---:|
| 14 August 2026 | 50 | $\$0.369326$ | $\$1.882281$ |
| 16 October 2026 | 39 | $\$0.171296$ | $\$3.380532$ |
| 15 January 2027 | 46 | $\$1.658747$ | $\$4.919979$ |

The longest maturity had the largest median and maximum deviation. This may reflect the greater effect of carry assumptions, dividend timing and exercise style over a longer horizon.

The residuals are not automatically arbitrage opportunities. The analysis uses midpoints rather than executable bid and ask combinations, and it does not include fees, financing or market impact. SPY options may also be exercised early, while the model uses a flat rate, a continuous dividend yield and potentially asynchronous spot and option observations.

Put–call parity is therefore best viewed here as a data and model-consistency check.

---

## 8. Limitations

The main limitations are:

- **European treatment of American-style options.** Early exercise can affect SPY calls around ex-dividend dates and sufficiently in-the-money puts.
- **Simplified carry assumptions.** A flat 4.0% rate and 1.2% continuous dividend yield replace maturity-specific rates and discrete distributions.
- **Midpoint pricing.** The bid–ask midpoint is a useful proxy but is not necessarily executable and can be unreliable for stale or wide markets.
- **Asynchronous data.** Spot and option quotes may not have updated at the same instant.
- **Single snapshot.** The results describe one market state and do not show how the surface changes through time.
- **No smoothing or arbitrage-free surface fit.** Quotes were calibrated independently and connected directly, without fitting a parametric surface or enforcing cross-strike and cross-maturity consistency.
- **Vendor-methodology uncertainty.** Yahoo Finance's precise calibration inputs and exercise assumptions are not available.

---

## 9. Conclusion

The implied-volatility solver calibrated all 378 retained SPY quotes successfully, demonstrating reliable numerical inversion on the selected dataset.

The calculated IVs broadly agreed with Yahoo Finance's values, but the residuals were structured by option type and maturity. Calls tended to calibrate below Yahoo's IVs, puts above them, and the separation increased with maturity.

A single constant volatility did not explain observed prices across strikes. All three expirations showed a clear downside skew, with the shortest maturity rising from approximately 15–17% near the forward to almost 40% on the downside.

The skew flattened as maturity increased, showing that volatility was both strike-dependent and term-dependent.

Put–call parity deviations highlighted imperfect consistency between the quote midpoints and the simplified European carry model, especially at the longest maturity. These deviations are better interpreted as evidence of data and modelling limitations than as direct arbitrage.

Overall, the numerical implementation worked as intended and produced results broadly consistent with vendor estimates. The recovered SPY surface nevertheless showed that correctness under Black–Scholes assumptions does not imply that constant volatility can explain the full market cross-section.
