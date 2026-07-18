# Monte Carlo Simulation for European Option Pricing

## 1. Introduction

Monte Carlo simulation prices an option by modelling many possible future outcomes for the underlying asset, calculating the option payoff in each outcome, and averaging those payoffs.

The central idea is:

> An option is worth the present value of its expected future payoff under the risk-neutral probability measure.

For a European option, the payoff depends only on the stock price at maturity. This makes Monte Carlo pricing especially simple because it is not necessary to simulate every intermediate stock price. The terminal stock price can be sampled directly from its known distribution.

Monte Carlo pricing is useful because it:

- is conceptually simple;
- works for complicated payoff functions;
- extends naturally to multiple assets and stochastic risk factors;
- provides a statistical measure of pricing uncertainty; and
- does not require the state space to be represented as a tree or grid.

Its main disadvantage is that convergence is relatively slow. The typical error decreases in proportion to

\[
\frac{1}{\sqrt{M}},
\]

where \(M\) is the number of simulations.

---

## 2. The Basic Intuition

Suppose a European call option has strike \(K\) and maturity \(T\). Its payoff at maturity is

\[
\max(S_T-K,0),
\]

where \(S_T\) is the stock price at maturity.

The future stock price is uncertain. Some simulated outcomes may finish below the strike and produce no payoff. Other outcomes may finish above the strike and produce a positive payoff.

For example, suppose five simulated terminal prices are:

| Simulation | Terminal stock price \(S_T\) | Call payoff \(\max(S_T-K,0)\) |
|---:|---:|---:|
| 1 | 92 | 0 |
| 2 | 101 | 1 |
| 3 | 108 | 8 |
| 4 | 115 | 15 |
| 5 | 84 | 0 |

If the strike is \(K=100\), the average payoff is

\[
\frac{0+1+8+15+0}{5}=4.8.
\]

However, this is the expected payoff at maturity, not its value today. The payoff must be discounted at the risk-free rate:

\[
V_0=e^{-rT}\times 4.8.
\]

A real Monte Carlo engine performs this calculation using tens of thousands or millions of simulated outcomes rather than five.

---

## 3. From Future Payoff to Present Value

Let an option have terminal payoff

\[
H(S_T).
\]

Examples include:

### European call

\[
H(S_T)=\max(S_T-K,0).
\]

### European put

\[
H(S_T)=\max(K-S_T,0).
\]

Under no-arbitrage assumptions, the option price is

\[
V_0=e^{-rT}\mathbb{E}^{\mathbb{Q}}\left[H(S_T)\right],
\]

where:

- \(V_0\) is the option value today;
- \(r\) is the continuously compounded risk-free rate;
- \(T\) is the time to maturity;
- \(\mathbb{Q}\) is the risk-neutral probability measure;
- \(\mathbb{E}^{\mathbb{Q}}\) denotes an expectation under that measure.

Monte Carlo simulation estimates this expectation numerically.

If \(S_T^{(1)},S_T^{(2)},\ldots,S_T^{(M)}\) are simulated terminal stock prices, then

\[
\widehat{V}_0
=
e^{-rT}
\frac{1}{M}
\sum_{i=1}^{M}
H\left(S_T^{(i)}\right).
\]

The symbol \(\widehat{V}_0\) indicates that this is an estimate of the true option value.

---

## 4. Why the Risk-Neutral Measure Is Used

A common source of confusion is why the stock's expected return does not appear in the pricing formula.

In the real world, an investor may believe that the stock will earn an expected return \(\mu\). Under the real-world probability measure, the stock may be modelled as

\[
dS_t=\mu S_t\,dt+\sigma S_t\,dW_t.
\]

However, an option is not priced by forecasting the investor's preferred estimate of \(\mu\). In an arbitrage-free market, the option can be replicated or hedged using the stock and a risk-free asset.

This leads to risk-neutral valuation. Under the risk-neutral measure, the stock's drift becomes the risk-free rate:

\[
dS_t=rS_t\,dt+\sigma S_t\,dW_t^{\mathbb{Q}}.
\]

The replacement of \(\mu\) with \(r\) does not mean investors are actually risk-neutral. It is a mathematical transformation that allows derivative prices to be calculated consistently with no-arbitrage conditions.

The effect is:

1. simulate the asset as though its expected continuously compounded growth rate is linked to \(r\);
2. calculate the expected payoff under that transformed probability distribution;
3. discount the expected payoff at the same risk-free rate.

---

## 5. Geometric Brownian Motion

The Black–Scholes framework assumes that the underlying asset follows geometric Brownian motion:

\[
dS_t=rS_t\,dt+\sigma S_t\,dW_t^{\mathbb{Q}},
\]

where:

- \(S_t\) is the stock price at time \(t\);
- \(r\) is the risk-free rate;
- \(\sigma\) is volatility;
- \(W_t^{\mathbb{Q}}\) is Brownian motion under the risk-neutral measure.

The model is called *geometric* Brownian motion because the random process applies to proportional changes in the asset price rather than absolute changes.

This has several important consequences:

- stock prices remain positive;
- continuously compounded returns are normally distributed;
- terminal stock prices are lognormally distributed;
- volatility scales with the square root of time.

---

## 6. Deriving the Terminal Stock Price

Starting from

\[
dS_t=rS_t\,dt+\sigma S_t\,dW_t^{\mathbb{Q}},
\]

apply Itô's lemma to \(\ln S_t\):

\[
d\ln S_t
=
\left(r-\frac{1}{2}\sigma^2\right)dt
+
\sigma\,dW_t^{\mathbb{Q}}.
\]

Integrating from \(0\) to \(T\) gives

\[
\ln S_T-\ln S_0
=
\left(r-\frac{1}{2}\sigma^2\right)T
+
\sigma W_T^{\mathbb{Q}}.
\]

Since

\[
W_T^{\mathbb{Q}}\sim N(0,T),
\]

it can be written as

\[
W_T^{\mathbb{Q}}=\sqrt{T}Z,
\qquad Z\sim N(0,1).
\]

Therefore,

\[
\ln\left(\frac{S_T}{S_0}\right)
=
\left(r-\frac{1}{2}\sigma^2\right)T
+
\sigma\sqrt{T}Z.
\]

Exponentiating both sides gives the exact terminal stock-price formula:

\[
\boxed{
S_T
=
S_0
\exp\left[
\left(r-\frac{1}{2}\sigma^2\right)T
+
\sigma\sqrt{T}Z
\right]
}
\]

This equation is the core of a Monte Carlo engine for European options.

---

## 7. Interpreting the Terminal-Price Formula

The formula can be separated into three components:

\[
S_T
=
S_0
\exp\left[
\underbrace{\left(r-\frac{1}{2}\sigma^2\right)T}_{\text{drift}}
+
\underbrace{\sigma\sqrt{T}Z}_{\text{random shock}}
\right].
\]

### 7.1 Initial stock price

\[
S_0
\]

is the known stock price today.

### 7.2 Risk-neutral drift

\[
\left(r-\frac{1}{2}\sigma^2\right)T
\]

controls the centre of the log-return distribution.

The term \(-\frac{1}{2}\sigma^2\) is the Itô correction. It ensures that the expected stock price is

\[
\mathbb{E}^{\mathbb{Q}}[S_T]=S_0e^{rT}.
\]

Without this correction, exponentiating a normally distributed return would introduce an extra upward bias because the exponential function is convex.

### 7.3 Random diffusion

\[
\sigma\sqrt{T}Z
\]

introduces uncertainty.

A larger \(\sigma\) produces a wider range of terminal stock prices. A longer maturity also produces greater dispersion, but uncertainty scales with \(\sqrt{T}\), not \(T\).

---

## 8. The Monte Carlo Pricing Algorithm

For a European option, the algorithm is:

1. Choose the number of simulations \(M\).
2. Generate independent standard-normal random variables:

   \[
   Z_1,Z_2,\ldots,Z_M\sim N(0,1).
   \]

3. Convert each draw into a terminal stock price:

   \[
   S_T^{(i)}
   =
   S_0
   \exp\left[
   \left(r-\frac{1}{2}\sigma^2\right)T
   +
   \sigma\sqrt{T}Z_i
   \right].
   \]

4. Calculate the terminal payoff for each simulation:

   \[
   H_i=H(S_T^{(i)}).
   \]

5. Average the payoffs:

   \[
   \overline{H}
   =
   \frac{1}{M}
   \sum_{i=1}^{M}H_i.
   \]

6. Discount the average payoff:

   \[
   \widehat{V}_0=e^{-rT}\overline{H}.
   \]

In pseudocode:

```text
generate M standard-normal random values

for each random value Z:
    calculate terminal stock price
    calculate terminal option payoff

price = discount factor * average payoff
```

A vectorised implementation performs these calculations on arrays rather than using a Python loop.

---

## 9. Why the Estimate Converges

Let

\[
X_i=e^{-rT}H(S_T^{(i)})
\]

be the discounted payoff from simulation \(i\).

The Monte Carlo estimate is the sample mean:

\[
\widehat{V}_0
=
\frac{1}{M}
\sum_{i=1}^{M}X_i.
\]

### 9.1 Law of large numbers

The law of large numbers states that, as \(M\) becomes large,

\[
\widehat{V}_0
\longrightarrow
\mathbb{E}^{\mathbb{Q}}[X].
\]

Therefore, the simulated price approaches the true risk-neutral option value.

### 9.2 Central limit theorem

For sufficiently large \(M\),

\[
\widehat{V}_0
\approx
N\left(
V_0,
\frac{\operatorname{Var}(X)}{M}
\right).
\]

This gives an approximate distribution for the simulation error.

The standard deviation of the estimator is

\[
\operatorname{SE}(\widehat{V}_0)
=
\frac{\sigma_X}{\sqrt{M}},
\]

where \(\sigma_X\) is the standard deviation of the discounted payoff.

Since the true \(\sigma_X\) is unknown, it is estimated using the sample standard deviation:

\[
\widehat{\operatorname{SE}}
=
\frac{s_X}{\sqrt{M}}.
\]

---

## 10. Standard Error and Confidence Intervals

The option price produced by Monte Carlo simulation is random. Running the engine with a different random seed will usually produce a slightly different value.

The standard error measures the uncertainty in the estimated mean:

\[
\widehat{\operatorname{SE}}
=
\frac{s_X}{\sqrt{M}}.
\]

An approximate 95% confidence interval is

\[
\widehat{V}_0
\pm
1.96\widehat{\operatorname{SE}}.
\]

More generally, for confidence level \(1-\alpha\),

\[
\widehat{V}_0
\pm
z_{1-\alpha/2}
\widehat{\operatorname{SE}},
\]

where \(z_{1-\alpha/2}\) is the relevant standard-normal critical value.

For example, suppose the Monte Carlo result is:

\[
\widehat{V}_0=10.47
\]

with

\[
\widehat{\operatorname{SE}}=0.03.
\]

Then the approximate 95% confidence interval is

\[
10.47\pm 1.96(0.03),
\]

or approximately

\[
[10.41,10.53].
\]

This interval quantifies simulation uncertainty. It does not account for uncertainty in the model assumptions, volatility estimate, interest rate, or market data.

---

## 11. The Rate of Convergence

Monte Carlo error decreases at the rate

\[
O\left(\frac{1}{\sqrt{M}}\right).
\]

This means that reducing the standard error by a factor of two requires approximately four times as many simulations.

For example:

| Simulations | Relative standard error scale |
|---:|---:|
| \(10{,}000\) | \(1\) |
| \(40{,}000\) | \(1/2\) |
| \(160{,}000\) | \(1/4\) |
| \(1{,}000{,}000\) | \(1/10\) |

This convergence rate is independent of the smoothness of the payoff and is one of Monte Carlo's main limitations.

By contrast, deterministic numerical methods may converge much faster for simple low-dimensional problems. Monte Carlo becomes more attractive as the number of risk factors increases because its convergence rate does not directly deteriorate with dimensionality in the same way as a multidimensional grid.

---

## 12. Random Seeds and Reproducibility

A pseudo-random number generator produces a deterministic sequence from an initial seed.

Using a fixed seed such as

```python
seed = 42
```

makes the simulation reproducible. The same inputs and seed produce the same random draws and therefore the same price.

This is useful for:

- unit tests;
- debugging;
- comparing code changes;
- producing repeatable analysis.

Using no fixed seed causes the simulation to generate a different estimate on each run. This is useful when studying the empirical distribution of the estimator but less useful for deterministic tests.

A seed does not make the simulation more accurate. It only controls reproducibility.

---

## 13. Variance Reduction

The most direct way to improve accuracy is to increase the number of simulations. However, because convergence is slow, it is often more efficient to reduce the variance of the estimator.

### 13.1 Antithetic variates

For each draw \(Z\), also use the draw \(-Z\).

The corresponding terminal stock prices are

\[
S_T^{+}
=
S_0
\exp\left[
\left(r-\frac{1}{2}\sigma^2\right)T
+
\sigma\sqrt{T}Z
\right],
\]

and

\[
S_T^{-}
=
S_0
\exp\left[
\left(r-\frac{1}{2}\sigma^2\right)T
-
\sigma\sqrt{T}Z
\right].
\]

The paired estimator is

\[
Y
=
\frac{1}{2}
\left[
e^{-rT}H(S_T^{+})
+
e^{-rT}H(S_T^{-})
\right].
\]

When one draw produces an unusually high terminal stock price, its antithetic partner tends to produce a lower terminal price. The errors partially offset one another.

The estimator remains unbiased, but its variance may be lower.

An important implementation detail is that the standard error must be calculated from the independent pair averages \(Y\), not by treating the two payoffs within each pair as independent observations.

### 13.2 Control variates

A control variate uses another random variable whose expected value is known.

For example, under the risk-neutral measure,

\[
\mathbb{E}^{\mathbb{Q}}[e^{-rT}S_T]=S_0.
\]

The discounted terminal stock price can therefore be used as a control.

Let

\[
X=e^{-rT}H(S_T)
\]

be the discounted option payoff, and let

\[
C=e^{-rT}S_T
\]

be the control variable, with known expectation

\[
\mathbb{E}[C]=S_0.
\]

A control-variate estimator is

\[
X_{\text{cv}}
=
X-\beta(C-S_0).
\]

The variance-minimising coefficient is

\[
\beta^*
=
\frac{\operatorname{Cov}(X,C)}
{\operatorname{Var}(C)}.
\]

If \(X\) and \(C\) are strongly correlated, the control variate can substantially reduce pricing error.

### 13.3 Other techniques

More advanced variance-reduction methods include:

- stratified sampling;
- Latin hypercube sampling;
- importance sampling;
- quasi-Monte Carlo methods;
- conditional Monte Carlo.

These methods preserve the core pricing logic while producing more informative samples.

---

## 14. Exact Terminal Sampling Versus Time-Stepped Simulation

For a European option under geometric Brownian motion, the terminal stock price can be sampled exactly:

\[
S_T
=
S_0
\exp\left[
\left(r-\frac{1}{2}\sigma^2\right)T
+
\sigma\sqrt{T}Z
\right].
\]

This should generally be preferred because it introduces no time-discretisation error.

A full path simulation divides maturity into \(N\) time steps:

\[
\Delta t=\frac{T}{N}.
\]

The exact transition over each step is

\[
S_{t+\Delta t}
=
S_t
\exp\left[
\left(r-\frac{1}{2}\sigma^2\right)\Delta t
+
\sigma\sqrt{\Delta t}Z_t
\right].
\]

Full paths are necessary when the payoff depends on the asset's history, such as:

- Asian options;
- barrier options;
- lookback options;
- options with path-dependent exercise rules;
- models with stochastic volatility or stochastic interest rates.

For a plain European call or put, simulating every intermediate point creates extra computation without adding pricing information.

---

## 15. Comparison With Black–Scholes

The Black–Scholes model gives a closed-form analytical price for a European call or put under its assumptions.

Monte Carlo simulation uses the same underlying risk-neutral model but estimates the expectation numerically.

For a sufficiently large number of simulations,

\[
V_{\text{MC}}
\approx
V_{\text{BS}}.
\]

Black–Scholes is preferable for a standard European option because it is:

- faster;
- deterministic;
- free from simulation error;
- available in closed form.

Monte Carlo is still valuable in this setting because it provides:

- a way to verify the implementation;
- a benchmark for convergence analysis;
- a foundation for pricing more complex derivatives;
- practice with statistical error estimation and variance reduction.

A useful validation is to check whether the Black–Scholes price lies within, or reasonably close to, the Monte Carlo confidence interval.

---

## 16. Comparison With the CRR Binomial Model

The Cox–Ross–Rubinstein model represents the stock price using a discrete recombining tree.

At each time step, the stock moves either up or down. The option is valued by backward induction using risk-neutral probabilities.

Monte Carlo instead generates complete random outcomes and averages their discounted payoffs.

### CRR strengths

- deterministic for fixed inputs and number of steps;
- supports backward induction;
- naturally handles American exercise;
- provides values throughout the tree.

### Monte Carlo strengths

- straightforward for high-dimensional problems;
- naturally handles complex path-dependent payoffs;
- easy to parallelise;
- provides explicit statistical uncertainty;
- requires memory proportional to the number of simulations rather than a multidimensional state grid.

### Key difference

CRR works backward from maturity through a discrete state tree. Monte Carlo works forward by sampling possible outcomes and averaging the resulting discounted payoffs.

Standard forward Monte Carlo does not naturally handle early exercise because the holder's decision depends on comparing immediate exercise with an unknown continuation value. Methods such as least-squares Monte Carlo are required for American-style options.

---

## 17. A Minimal Mathematical Implementation

The main quantities are:

### Discount factor

\[
D=e^{-rT}.
\]

### Drift

\[
a=
\left(r-\frac{1}{2}\sigma^2\right)T.
\]

### Diffusion scale

\[
b=\sigma\sqrt{T}.
\]

### Random draws

\[
Z_i\sim N(0,1).
\]

### Terminal prices

\[
S_T^{(i)}=S_0e^{a+bZ_i}.
\]

### Payoffs

For a call:

\[
H_i=\max(S_T^{(i)}-K,0).
\]

For a put:

\[
H_i=\max(K-S_T^{(i)},0).
\]

### Price estimate

\[
\widehat{V}_0
=
D\frac{1}{M}\sum_{i=1}^{M}H_i.
\]

### Estimated standard error

\[
\widehat{\operatorname{SE}}
=
\frac{
\operatorname{sd}(DH_1,\ldots,DH_M)
}{
\sqrt{M}
}.
\]

---

## 18. Implementation Structure

A clean Monte Carlo model can separate the calculation into the following responsibilities:

```text
MonteCarloModel
├── discount_factor
├── terminal_drift
├── terminal_diffusion_scale
├── generate_standard_normal_draws
├── terminal_stock_prices
├── terminal_payoffs
├── discounted_payoffs
├── standard_error
├── confidence_interval
├── simulate
└── price
```

This structure makes each mathematical component independently testable.

For example:

- `terminal_drift` can be checked against the formula;
- `terminal_stock_prices` can be tested using fixed normal draws;
- `terminal_payoffs` can be tested with known prices above and below the strike;
- `standard_error` can be tested on a small known array;
- `simulate` can be tested for reproducibility with a fixed seed.

---

## 19. Testing the Model

### 19.1 Reproducibility test

Two models with the same inputs and seed should produce the same result.

```python
result_1 = model_1.simulate()
result_2 = model_2.simulate()

assert result_1 == result_2
```

### 19.2 Payoff test

For a call with strike \(100\), terminal prices

\[
[80,100,120]
\]

should produce payoffs

\[
[0,0,20].
\]

For a put, they should produce

\[
[20,0,0].
\]

### 19.3 Distribution test

The simulated discounted terminal stock price should have a sample mean close to the initial spot:

\[
e^{-rT}
\frac{1}{M}
\sum_{i=1}^{M}S_T^{(i)}
\approx S_0.
\]

### 19.4 Black–Scholes comparison

The Monte Carlo estimate should be statistically consistent with the Black–Scholes price.

One possible test is

\[
\left|
\widehat{V}_{\text{MC}}-V_{\text{BS}}
\right|
\leq
c\widehat{\operatorname{SE}},
\]

where \(c\) might be chosen as \(3\) or \(4\) to avoid making the test too sensitive to a rare random sample.

A fixed tolerance can make stochastic tests unreliable. A tolerance based on the estimated standard error is better aligned with the behaviour of the simulation.

---

## 20. Common Mistakes

### Using the real-world expected return

The risk-neutral drift should use \(r\), not an estimate of the stock's expected return \(\mu\).

### Forgetting the Itô correction

The log-price drift is

\[
r-\frac{1}{2}\sigma^2,
\]

not simply \(r\).

### Forgetting to discount

The average payoff is measured at maturity. It must be multiplied by

\[
e^{-rT}.
\]

### Using variance instead of standard deviation

The standard error is

\[
\frac{s}{\sqrt{M}},
\]

not

\[
\frac{s^2}{\sqrt{M}}.
\]

### Using population standard deviation

When estimating uncertainty from simulated observations, the sample standard deviation normally uses one degree-of-freedom correction.

In NumPy:

```python
np.std(samples, ddof=1)
```

### Assuming more simulations remove model error

More simulations reduce sampling error but do not correct inaccurate assumptions about volatility, interest rates, dividends, jumps, liquidity, or the asset-price process.

### Simulating unnecessary time steps

For a path-independent European option under geometric Brownian motion, direct terminal sampling is exact and more efficient.

---

## 21. Limitations of the Basic Model

The basic simulation inherits the assumptions of Black–Scholes:

- constant volatility;
- constant risk-free rate;
- frictionless trading;
- no arbitrage;
- continuous trading;
- lognormal stock prices;
- no jumps;
- European exercise;
- no dividends unless explicitly included.

A more realistic model may add:

- a continuous dividend yield;
- discrete dividends;
- local volatility;
- stochastic volatility;
- stochastic interest rates;
- jumps;
- multiple correlated assets;
- transaction costs or liquidity adjustments.

Monte Carlo is flexible enough to accommodate many of these extensions, although the simulation and calibration become more complex.

---

## 22. Extension for a Continuous Dividend Yield

If the stock pays a continuous dividend yield \(q\), the risk-neutral process becomes

\[
dS_t=(r-q)S_t\,dt+\sigma S_t\,dW_t^{\mathbb{Q}}.
\]

The terminal stock price is then

\[
S_T
=
S_0
\exp\left[
\left(r-q-\frac{1}{2}\sigma^2\right)T
+
\sigma\sqrt{T}Z
\right].
\]

The option payoff is still discounted at the risk-free rate:

\[
V_0=e^{-rT}\mathbb{E}^{\mathbb{Q}}[H(S_T)].
\]

The dividend yield changes the stock's risk-neutral drift but not the payoff discount factor.

---

## 23. Summary

Monte Carlo option pricing converts a theoretical expectation into a numerical average.

The full logic is:

1. Under no arbitrage, an option price is the discounted risk-neutral expected payoff.
2. Under geometric Brownian motion, the terminal stock price has an exact lognormal distribution.
3. Standard-normal random draws can therefore be transformed into possible terminal stock prices.
4. The option payoff is calculated for each simulated terminal price.
5. The discounted average payoff estimates the option value.
6. The standard error measures the remaining simulation uncertainty.
7. The estimator converges at a rate proportional to \(1/\sqrt{M}\).
8. Variance-reduction methods can improve precision without relying only on more simulations.

For a European call or put, Monte Carlo is not the fastest pricing method because Black–Scholes provides a closed-form solution. Its value is that the same framework can be extended to derivatives whose payoffs or underlying dynamics are too complex for an analytical formula.