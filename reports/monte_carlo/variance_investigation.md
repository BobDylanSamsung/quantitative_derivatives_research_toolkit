# QR-10 Monte Carlo Variance Investigation

## 1. Executive summary

This investigation tested how the accuracy and uncertainty of a Monte Carlo European call option price change as the number of simulated terminal stock prices increases.

Three one-year call options were studied under the same market assumptions:

| Scenario | Spot | Strike | Risk-free rate | Volatility | Maturity |
|---|---:|---:|---:|---:|---:|
| In the money (ITM) | 100 | 80 | 5% | 20% | 1 year |
| At the money (ATM) | 100 | 100 | 5% | 20% | 1 year |
| Out of the money (OTM) | 100 | 120 | 5% | 20% | 1 year |

For each scenario, Monte Carlo estimates were generated at nine simulation counts ranging from 100 to 1,000,000. Each simulation count was repeated 50 times with different random seeds. The closed-form Black-Scholes price was used as the exact benchmark under the assumptions of the model.

The main findings were:

1. The empirical variance of the Monte Carlo price estimator decreased approximately as $N^{-1}$, as predicted by theory.
2. The standard error, root mean squared error, and confidence-interval half-width decreased approximately as $N^{-1/2}$.
3. Increasing the number of simulations reduced the typical size of the error, but the price estimate did not converge monotonically because each estimate was based on a random sample.
4. The 95% confidence intervals generally achieved coverage close to their nominal 95% level. The main exception was the OTM option at only 100 simulations, where coverage was 80%.
5. A target 95% confidence-interval half-width of $0.01 was not reached by the largest tested count of 1,000,000 simulations.
6. Pilot estimates indicated that approximately 14.17 million ITM simulations, 8.38 million ATM simulations, and 2.95 million OTM simulations would be required to achieve the one-cent absolute half-width target.

The results therefore support the theoretical Monte Carlo convergence relationships and show the high computational cost of demanding very small absolute pricing uncertainty from a basic Monte Carlo estimator.

---

## 2. Research questions

The ticket posed two main research questions:

1. **How many simulations are required?**
2. **How does variance decrease as the number of simulations increases?**

The first question does not have a universal answer. A simulation count is only sufficient relative to a defined accuracy requirement.

In this investigation, the accuracy requirement was defined as:

> The minimum number of simulations required to produce a 95% confidence interval with a half-width no greater than $0.01.

A half-width of $0.01 means that the confidence interval is approximately two cents wide in total:

$$\widehat V_N - 0.01,\ \widehat V_N + 0.01$$

The second question was investigated by measuring how the variance of independently repeated Monte Carlo price estimates changed with the number of simulations.

---

## 3. Monte Carlo price estimator

Under the risk-neutral geometric Brownian motion model, a terminal stock price is simulated as
$$S_T=S_0\exp\left[\left(r-\frac{1}{2}\sigma^2\right)T+\sigma\sqrt{T}Z\right],
\qquad Z\sim N(0,1).
$$

For a European call option, the terminal payoff is

$$
H(S_T)=\max(S_T-K,0).
$$

The discounted payoff from simulation $i$ is

$$
X_i=e^{-rT}H(S_T^{(i)}).
$$

Given $N$ independent simulations, the Monte Carlo price estimator is the sample mean

$$
\widehat V_N
=
\frac{1}{N}
\sum_{i=1}^{N}X_i.
$$

The true model price is

$$
V
=
\mathbb E^{\mathbb Q}[X].
$$

Under the same assumptions, the Black-Scholes formula evaluates this expectation analytically. The Black-Scholes value can therefore be treated as the exact benchmark when testing the Monte Carlo implementation.

---

## 4. Why repeated experiments are necessary

One Monte Carlo run at each simulation count is enough to show a possible convergence path, but it is not enough to measure the variance of the estimator.

For a fixed $N$, repeating the entire pricing calculation with different random seeds produces estimates

$$
\widehat V_{N,1},
\widehat V_{N,2},
\ldots,
\widehat V_{N,R},
$$

where $R=50$ in this experiment.

The empirical variance across these repeated estimates is

$$
\widehat{\operatorname{Var}}(\widehat V_N)
=
\frac{1}{R-1}
\sum_{j=1}^{R}
\left(
\widehat V_{N,j}
-
\overline V_N
\right)^2,
$$

where

$$
\overline V_N
=
\frac{1}{R}
\sum_{j=1}^{R}\widehat V_{N,j}.
$$

This quantity measures how much the final estimated option price would vary if the entire Monte Carlo experiment were repeated.

It is important to distinguish this from the variance of individual discounted payoffs. Individual option payoffs can have substantial dispersion. The variance of their sample mean is much smaller because averaging reduces uncertainty.

---

## 5. Theoretical convergence

Let

$$
\sigma_X^2=\operatorname{Var}(X)
$$

be the variance of one discounted payoff.

Because the Monte Carlo estimator is the average of $N$ independent discounted payoffs,

$$
\operatorname{Var}(\widehat V_N)
=
\frac{\sigma_X^2}{N}.
$$

Therefore, estimator variance should decrease as

$$
\operatorname{Var}(\widehat V_N)=O(N^{-1}).
$$

The estimator's standard deviation, usually called its standard error, is

$$
\operatorname{SE}(\widehat V_N)
=
\frac{\sigma_X}{\sqrt N}.
$$

Therefore,

$$
\operatorname{SE}(\widehat V_N)=O(N^{-1/2}).
$$

The practical consequence is that Monte Carlo converges slowly:

- doubling the number of simulations reduces standard error by a factor of only $\frac 1 {\sqrt 2}$
- halving the standard error requires approximately four times as many simulations
- reducing the standard error by a factor of ten requires approximately one hundred times as many simulations

---

## 6. Experimental design

The tested simulation counts were

$$
100,\ 300,\ 1{,}000,\ 3{,}000,\ 10{,}000,\ 30{,}000,\ 100{,}000,\ 300{,}000,\ 1{,}000{,}000.
$$

These counts are approximately logarithmically spaced. This is appropriate because the investigation covers four orders of magnitude and the expected convergence relationships are power laws.

For each scenario and simulation count:

1. A new Monte Carlo model was created.
2. A deterministic seed was assigned.
3. Terminal stock prices were generated.
4. Discounted option payoffs were calculated.
5. Their sample mean was recorded as the option-price estimate.
6. The estimated standard error was calculated.
7. A 95% normal-approximation confidence interval was constructed.
8. The estimate was compared with the Black-Scholes benchmark.
9. The run time was recorded.
10. The entire calculation was repeated 50 times.

The experiment generated

$$
3 \times 9 \times 50 = 1{,}350
$$

independent pricing runs in total.

The same seed schedule was reused across the ITM, ATM, and OTM scenarios. This means corresponding runs across scenarios used the same underlying standard-normal draws. This is acceptable and can make scenario comparisons less noisy, but it should be documented explicitly.

---

## 7. Metrics recorded

### 7.1 Bias

Bias was estimated as

$$
\text{bias}
=
\overline V_N-V_{\text{BS}}.
$$

A positive value means that the mean Monte Carlo estimate was above the Black-Scholes benchmark. A negative value means it was below.

The basic Monte Carlo sample mean is theoretically unbiased under exact terminal sampling. Small observed biases are expected because only 50 repeated estimates were averaged.

### 7.2 Empirical variance

The empirical variance is the sample variance of the 50 Monte Carlo prices at a fixed simulation count.

This is the primary quantity used to answer how estimator variance decreases.

### 7.3 Estimated standard error

Within each individual Monte Carlo run, the standard error was estimated using

$$
\widehat{\operatorname{SE}}
=
\frac{s_X}{\sqrt N},
$$

where $s_X$ is the sample standard deviation of that run's discounted payoffs.

### 7.4 Estimated estimator variance

The code records

$$
\widehat{\operatorname{Var}}(\widehat V_N)
=
\widehat{\operatorname{SE}}^2.
$$

This is an internal estimate from one run. It can be compared with the empirical variance across repeated runs.

### 7.5 Root mean squared error

The root mean squared error was calculated as

$$
\operatorname{RMSE}
=
\sqrt{
\frac{1}{R}
\sum_{j=1}^{R}
\left(
\widehat V_{N,j}-V_{\text{BS}}
\right)^2
}.
$$

RMSE measures the typical total error relative to the benchmark. It incorporates both variance and bias:

$$
\operatorname{MSE}
=
\operatorname{Var}(\widehat V_N)
+
\operatorname{Bias}(\widehat V_N)^2.
$$

Because the estimator is approximately unbiased, RMSE should decrease at roughly the same $N^{-1/2}$ rate as standard error.

### 7.6 Confidence-interval coverage

Each run produced a 95% interval

$$
\widehat V_N
\pm
1.96\widehat{\operatorname{SE}}.
$$

Coverage was recorded as `True` when the interval contained the Black-Scholes benchmark.

The empirical coverage rate is

$$
\frac{\text{number of intervals containing }V_{\text{BS}}}{R}.
$$

For a correctly calibrated 95% confidence interval, this rate should be near 0.95 over many repeated experiments.

With only 50 repetitions, coverage moves in increments of 0.02. Values such as 0.92, 0.96, or 0.98 are therefore not surprising.

---

## 8. Black-Scholes benchmarks

The analytical prices were:

| Scenario | Black-Scholes price |
|---|---:|
| ITM | 24.588835 |
| ATM | 10.450584 |
| OTM | 3.247477 |

These values are the exact prices under the assumed Black-Scholes model and are used only as numerical benchmarks. They do not imply that the model perfectly represents market prices in practice.

---

## 9. Selected convergence results

The following table shows selected results at 100, 10,000, and 1,000,000 simulations.

| Scenario | Simulations | Mean MC price | Bias | Empirical variance | Mean standard error | Mean 95% CI half-width | RMSE | Coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ITM | 100 | 24.983624 | 0.394789 | 3.713005 | 1.884240 | 3.693042 | 1.947974 | 96% |
| ITM | 10,000 | 24.613481 | 0.024645 | 0.031223 | 0.191686 | 0.375698 | 0.176651 | 98% |
| ITM | 1,000,000 | 24.590557 | 0.001721 | 0.000381 | 0.019163 | 0.037559 | 0.019408 | 96% |
| ATM | 100 | 10.605890 | 0.155306 | 2.468593 | 1.449757 | 2.841471 | 1.563119 | 92% |
| ATM | 10,000 | 10.465459 | 0.014875 | 0.020331 | 0.147331 | 0.288763 | 0.141935 | 96% |
| ATM | 1,000,000 | 10.452494 | 0.001911 | 0.000221 | 0.014721 | 0.028852 | 0.014829 | 98% |
| OTM | 100 | 3.224298 | -0.023179 | 1.118798 | 0.834257 | 1.635114 | 1.047358 | 80% |
| OTM | 10,000 | 3.256143 | 0.008665 | 0.006985 | 0.086821 | 0.170167 | 0.083191 | 98% |
| OTM | 1,000,000 | 3.248395 | 0.000917 | 0.000070 | 0.008673 | 0.016999 | 0.008324 | 96% |

Several features are visible.

First, the mean Monte Carlo prices approach the Black-Scholes values. The estimates do not move monotonically because each point is affected by random sampling error.

Second, the size of the uncertainty falls dramatically. For the ATM option, the mean confidence-interval half-width fell from approximately 2.84 at 100 simulations to approximately 0.0289 at 1,000,000 simulations.

The simulation count increased by a factor of 10,000:

$$
\frac{1{,}000{,}000}{100}=10{,}000.
$$

The square root of this increase is 100, so theory predicts that standard error should fall by a factor of approximately 100. The ATM standard error fell from 1.4498 to 0.01472, a factor of approximately 98.5, which is close to the theoretical prediction.

---

## 10. Estimated convergence rates

To estimate the convergence rate, the experiment fitted regressions in log-log space.

If a metric follows

$$
Y_N=cN^b,
$$

then taking logarithms gives

$$
\log Y_N=\log c+b\log N.
$$

The slope $b$ can therefore be estimated with linear regression.

The results were:

| Scenario | Metric | Estimated slope | Theoretical slope | $R^2$ |
|---|---|---:|---:|---:|
| ATM | Empirical variance | -1.0352 | -1.0 | 0.9969 |
| ATM | Mean standard error | -0.4990 | -0.5 | 1.0000 |
| ATM | RMSE | -0.5145 | -0.5 | 0.9977 |
| ATM | CI half-width | -0.4990 | -0.5 | 1.0000 |
| ITM | Empirical variance | -1.0217 | -1.0 | 0.9981 |
| ITM | Mean standard error | -0.4988 | -0.5 | 1.0000 |
| ITM | RMSE | -0.5099 | -0.5 | 0.9986 |
| ITM | CI half-width | -0.4988 | -0.5 | 1.0000 |
| OTM | Empirical variance | -1.0483 | -1.0 | 0.9973 |
| OTM | Mean standard error | -0.4972 | -0.5 | 1.0000 |
| OTM | RMSE | -0.5208 | -0.5 | 0.9977 |
| OTM | CI half-width | -0.4972 | -0.5 | 1.0000 |

These results provide strong empirical support for the theoretical convergence rates.

The empirical variance slopes ranged from approximately -1.02 to -1.05, close to the predicted -1.

The standard-error slopes ranged from approximately -0.497 to -0.499, extremely close to the predicted -0.5.

The confidence-interval half-width has the same slope as standard error because it is a constant critical value multiplied by the standard error.

The very high $R^2$ values indicate that the power-law relationship explains nearly all of the variation across the tested simulation counts.

The empirical variance slope is slightly noisier than the standard-error slope because it is estimated from only 50 repeated prices at each count. The standard error, by contrast, is estimated using every discounted payoff within each run and then averaged across repetitions.

---

## 11. Confidence-interval coverage

Average coverage across all tested simulation counts was approximately:

| Scenario | Average empirical coverage |
|---|---:|
| ITM | 95.8% |
| ATM | 95.8% |
| OTM | 94.0% |

These results are close to the intended 95% level.

The OTM option at 100 simulations had only 80% coverage. This is the clearest sign of poor small-sample normal approximation.

An OTM call has many zero payoffs and a smaller number of positive, right-skewed payoffs. With only 100 simulations, some samples may contain too few positive observations to estimate the shape and variance of the payoff distribution reliably. The distribution of the sample mean may therefore not yet be sufficiently close to normal.

Coverage improved to 92% at 300 simulations and remained between 94% and 98% from 1,000 simulations onward.

The coverage values at large $N$ sometimes exceeded 95%, but this does not imply that the intervals are necessarily too wide. With 50 repetitions, the sampling standard deviation of an observed 95% coverage proportion is approximately

$$
\sqrt{\frac{0.95(0.05)}{50}}
\approx 0.0308.
$$

An observed coverage of 92% or 98% is therefore within roughly one sampling standard deviation of the target.

A future report could add a binomial Wilson confidence interval around each empirical coverage rate to make this uncertainty explicit.

---

## 12. How many simulations are required?

### 12.1 Derivation

For a target confidence-interval half-width $h$,

$$
h
=
z_{1-\alpha/2}
\frac{\sigma_X}{\sqrt N}.
$$

Rearranging,

$$
N
=
\left(
\frac{z_{1-\alpha/2}\sigma_X}{h}
\right)^2.
$$

Because $\sigma_X$ is unknown, the experiment ran a pilot simulation with 10,000 paths and estimated the standard deviation of the discounted payoff.

For a 95% interval,

$$
z_{1-\alpha/2}\approx1.96.
$$

The target was

$$
h=0.01.
$$

### 12.2 Pilot estimates

| Scenario | Pilot price | Estimated discounted-payoff SD | Estimated simulations required |
|---|---:|---:|---:|
| ITM | 24.448483 | 19.207372 | 14,172,031 |
| ATM | 10.345182 | 14.766266 | 8,376,017 |
| OTM | 3.238218 | 8.757690 | 2,946,289 |

The ITM option required the largest number of simulations under an absolute one-cent target because its discounted payoff had the greatest standard deviation.

The OTM option required the fewest simulations in absolute price units because its discounted payoff standard deviation was lower.

This does not mean that the OTM estimate is more precise in relative terms. At 1,000,000 simulations:

- ITM half-width as a percentage of price was approximately 0.153%;
- ATM half-width as a percentage of price was approximately 0.276%;
- OTM half-width as a percentage of price was approximately 0.523%.

The OTM option therefore had the widest confidence interval relative to its much smaller option value.

This demonstrates why the precision criterion must be stated clearly. Absolute and relative error targets can lead to different conclusions about which option is hardest to estimate.

### 12.3 Why the observed result was `None`

The largest tested count was 1,000,000 simulations. At that point, the mean half-widths were:

| Scenario | Half-width at 1,000,000 simulations |
|---|---:|
| ITM | 0.037559 |
| ATM | 0.028852 |
| OTM | 0.016999 |

All three remained above the $0.01 target. The `find_observed_required_simulations` function therefore returned `None` for every scenario.

This is not a failure of the function and does not mean the experiment produced no answer. It means the tested range did not extend far enough to validate the chosen target empirically.

The pilot calculation provides estimated requirements, but the experiment should either:

1. extend the simulation grid beyond the predicted requirements; or
2. choose a less demanding target that can be reached within the existing grid.

For example, with an absolute half-width target of $0.05, the first tested counts satisfying the precision requirement would be approximately:

| Scenario | First tested count with mean half-width $\leq 0.05$ |
|---|---:|
| ITM | 1,000,000 |
| ATM | 1,000,000 |
| OTM | 300,000 |

A target should not be changed solely to force a successful result, but the experiment range and target should be chosen consistently.

---

## 13. Interpretation of the plots

### 13.1 Price-convergence plots

The price-convergence plots show one Monte Carlo estimate and its confidence interval at each simulation count, together with the Black-Scholes benchmark.

The intervals narrow as $N$ increases, and the estimates cluster increasingly close to the benchmark.

The line should not be interpreted as a deterministic convergence path. In the current implementation, different simulation counts use different seeds and therefore different independent samples. The estimate at 300 simulations is not formed by adding 200 paths to the 100-simulation estimate.

For a genuine cumulative convergence path, one large random sample should be generated and the estimates should be computed from nested prefixes of that same sample.

Alternatively, the plot could show the mean Monte Carlo price across all 50 repetitions at each count, with error bars based on empirical variation. This would align more directly with the repeated-experiment methodology.

### 13.2 Variance-convergence plots

The empirical variance lines closely track the reference $N^{-1}$ lines. The small deviations and local irregularities are expected because each empirical variance is estimated from only 50 repeated prices.

The log-log scale is essential. A power law appears as a straight line, and the slope can be interpreted directly as the convergence exponent.

### 13.3 Error-convergence plots

The mean estimated standard error and empirical RMSE both closely track the $N^{-1/2}$ reference.

They are not identical:

- standard error is estimated from the payoff samples inside each run;
- RMSE is calculated from the deviations of repeated price estimates from the Black-Scholes benchmark.

Their agreement indicates that the estimator has little bias and that the internal standard-error calculation is consistent with observed pricing error.

### 13.4 Coverage plots

The coverage plots fluctuate around 95% rather than converging smoothly. This is expected because each point is a proportion based on only 50 binary outcomes.

The OTM result at 100 simulations is materially low and should be discussed as a limitation of the normal approximation for a sparse and skewed payoff distribution.

---

## 14. Final conclusions

The investigation successfully answered how Monte Carlo variance decreases.

Across ITM, ATM, and OTM call options:

$$
\operatorname{Var}(\widehat V_N)
\approx
O(N^{-1}),
$$

and

$$
\operatorname{SE}(\widehat V_N)
\approx
O(N^{-1/2}).
$$

The estimated slopes were close to their theoretical values, with high $R^2$, and the RMSE followed the same square-root convergence relationship.

The confidence intervals generally achieved coverage close to 95%, supporting the correctness of the standard-error implementation. The poor 80% OTM coverage at 100 simulations demonstrates that a normal interval can be unreliable for very small samples and highly skewed payoff distributions.

The question of how many simulations are required was answered relative to an explicit one-cent half-width target. Pilot estimates indicated requirements of approximately:

- 14.17 million paths for the ITM call;
- 8.38 million paths for the ATM call;
- 2.95 million paths for the OTM call.

Because the experiment stopped at one million paths, none of these requirements was directly observed. The next step is to extend the tested range or select a target consistent with the available computational budget.

Overall, the methodology is statistically sound and the results strongly support Monte Carlo convergence theory. The main remaining work is to improve presentation, display the convergence-rate results, align the target with the simulation grid, and add runtime analysis.
