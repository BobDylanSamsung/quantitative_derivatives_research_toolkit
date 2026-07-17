# Cox-Ross-Rubinstein (CRR) Binomial Tree Model

- Introduced by John Cox, Stephen Ross and Mark Rubinstein (1979).
- Prices European and American options by modelling the underlying asset as a recombining binomial tree.
- Rather than solving a differential equation analytically, the option value is obtained through **backward induction** on a discrete lattice.
- As the number of time steps increases,

$$
\lim_{N\to\infty}V_{CRR}=V_{BS}
$$

under the Black-Scholes assumptions.

---

# Assumptions

- The underlying asset follows a **binomial process** over each discrete time interval.
- Trading is frictionless (no transaction costs or taxes).
- The risk-free interest rate is known and constant.
- Volatility is known and constant.
- Short selling is permitted.
- Markets are arbitrage free.
- The underlying pays no dividends.
- The option is European and can only be exercised at expiration.

---

# Variables

- $V$ = Option value
- $S_0$ = Current stock price
- $S_j$ = Stock price at terminal node $j$
- $K$ = Strike price
- $r$ = Risk-free interest rate
- $T$ = Time to expiry
- $\sigma$ = Volatility
- $N$ = Number of time steps
- $\Delta t = \frac{T}{N}$
- $u$ = Upward price multiplier
- $d$ = Downward price multiplier
- $p$ = Risk-neutral probability of an up move

---

# Tree Parameters

Each time step has duration

$$
\Delta t=\frac{T}{N}
$$

The stock either moves up

$$
u=e^{\sigma\sqrt{\Delta t}}
$$

or down

$$
d=e^{-\sigma\sqrt{\Delta t}}=\frac1u
$$

After $j$ up moves,

$$
S_j=S_0u^jd^{N-j}
$$

or equivalently (using $d=1/u$),

$$
S_j=S_0u^{2j-N}.
$$

---

# Risk-Neutral Probability

Unlike a real probability, the CRR probability is chosen so that the expected return equals the risk-free rate.

The expected stock price one step ahead satisfies

$$
E[S_{t+\Delta t}]
=
S_te^{r\Delta t}.
$$

Substituting the binomial outcomes,

$$
pu+(1-p)d=e^{r\Delta t}
$$

giving

$$
p=
\frac{e^{r\Delta t}-d}
{u-d}.
$$

---

# Terminal Payoff

### Call

$$
V_N=\max(S_j-K,0)
$$

### Put

$$
V_N=\max(K-S_j,0).
$$

---

# Backward Induction

Each node value equals the discounted expected value of its children under the risk-neutral measure.

$$
V
=
e^{-r\Delta t}
\left(
pV_u
+
(1-p)V_d
\right).
$$

Repeatedly applying this equation eventually produces the option value at the root node.

---

# Tree Structure

For a three-step tree:

```text
                    S₀

              /             \

          Su                 Sd

       /      \          /       \

    Suu      Sud==Sdu      Sdd

    /  \      /  \         /  \

Suuu Suud Sudd Sddd
```

The important property is that

$$
ud=1
$$

which implies

$$
Sud=Sdu.
$$

The tree therefore **recombines**.

Instead of $2^N$ terminal paths, there are only $N+1$ distinct terminal stock prices.

---

# Intuition

The model assumes that over a sufficiently small time interval, a stock can only move in one of two directions:

- Up by a factor $u$
- Down by a factor $d$

Although this seems simplistic, increasing the number of time steps allows the tree to approximate continuous stock-price evolution.

The option value is obtained by working **backwards**:

1. Compute every possible payoff at expiration.
2. At each preceding node, replace the two future payoffs by their discounted expected value.
3. Continue until only a single value remains.

Unlike Black-Scholes, CRR does **not** require solving a differential equation. Instead, it numerically constructs the replicating portfolio implied by no-arbitrage.

---

# Mathematical Intuition

At every node, the option value satisfies

$$
V=\Delta S+B
$$

where

- $\Delta$ shares of stock are held.
- $B$ is invested in the risk-free asset.

Choosing $\Delta$ and $B$ so that the portfolio matches the option value in both the up and down states gives

$$
\Delta
=
\frac{V_u-V_d}
{S_u-S_d}
$$

and

$$
B
=
e^{-r\Delta t}
\frac{uV_d-dV_u}
{u-d}.
$$

Substituting these into

$$
V=\Delta S+B
$$

yields the familiar risk-neutral pricing equation

$$
V
=
e^{-r\Delta t}
\left(
pV_u+(1-p)V_d
\right).
$$

Thus, the risk-neutral probability is **not** an assumption—it is a consequence of constructing a perfectly hedged portfolio under the no-arbitrage principle.

---

# Advantages

- Works for both European and American options.
- Easily extended to options with dividends.
- Simple numerical implementation.
- Converges to the Black-Scholes price as $N\to\infty$.
- Provides intuition for delta hedging and replication.

---

# Limitations

- Requires many time steps for high accuracy.
- Computational complexity is

$$
O(N^2)
$$

although memory usage can be reduced to

$$
O(N)
$$

using backward induction.

- Convergence is slower than analytical Black-Scholes.
- Assumes constant volatility and interest rates.

---

# Relationship to Black-Scholes

The CRR model can be viewed as a discrete approximation to the Black-Scholes model.

As

$$
\Delta t\to0
$$

or equivalently

$$
N\to\infty,
$$

the binomial random walk converges to **geometric Brownian motion**, and the CRR pricing equation converges to the Black-Scholes solution.

This makes the CRR model not just another pricing method, but a constructive numerical approximation to Black-Scholes that naturally extends to pricing **American-style options**, where no closed-form Black-Scholes solution exists.