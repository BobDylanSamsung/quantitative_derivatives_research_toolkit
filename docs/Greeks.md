Unlike stocks who's prices are based on supply and demand, options have internal factors that determine their value including time until contract expiry, market volatility and changes in the price of the underlying stock. Mathematical gauges called the Greeks help measure and manage an options risk. 

- Delta - Measures impact of a change in the price of an underlying asset
- Gamma - Measures the rate of change of delta
- Theta - Measures the impact of a change in time remaining
- Vega - Measures the impact of a change in volatility

# Summary
$$\begin{aligned}
\Delta_C&=N(d_1)\\
\Delta_P&=N(d_1)-1\\
\\
\Gamma&=\frac{\partial^2C}{\partial S^2}\\
&=\frac 1{S\sigma\sqrt t}N'(d_1)\\
\\
\Theta &= -\frac{\partial C}{\partial t}\\\\
\Theta_C &= -\frac{S N'(d_1)\sigma}{2\sqrt{T}} -rKe^{-rT}N(d_2) \\[1ex] \Theta_P &= -\frac{S N'(d_1)\sigma}{2\sqrt{T}} +rKe^{-rT}N(-d_2)\\
\\
V&=\frac{\partial C}{\partial\sigma}\\
&=S\sqrt t N'(d_1)
\end{aligned}$$
Where
$$\begin{aligned}
N(x) &= \frac 1 {\sqrt{2\pi}}\int_{-\infty}^x e^{-\frac{t^2}{2}}dt\\
N'(x)&=\frac 1 {\sqrt{2\pi}} e^{-\frac{t^2}{2}}
\end{aligned}$$
are the CDF and PDF respectively
## Delta
Delta is considered the most important of the Greeks and measures the rate of change between the options price and a $1 change in the underlying assets price.

- Delta tends to increase closer to expiration for near or at-the-money options.
- Delta can also be assessed with gamma, a measure of delta's rate of change.
- Delta also reacts to changes in implied volatility.

The values of a delta depend on if the option is a call or a put:
- $\Delta_{call}\in(0,1)$ 
- $\Delta_{put}\in(-1,0)$ 

Eg: if you own a call option with a delta of 0.3 and the stock price increases by $1, the option should gain about 30 cents in value. Whereas the opposite occurs if the stock falls and you would lose 30 cents.

Traders use delta as a gauge of the probability that an option will be ITM at expiration:
- A call option with a 0.30 delta suggests about a 30% chance of being ITM at expiration.
- A call option with a 0.70 delta suggests about a 70% chance of being ITM at expiration.
- At-the-money options typically have deltas around 0.50, suggesting a 50/50 chance.

| Delta Value | Option Type | Moneyness | Approximate Probability ITM |
|-------------|-------------|-----------|-----------------------------|
| 1.0         | Call        | Deep ITM  | ~100%                       |
| 0.8         | Call        | ITM       | ~75%                        |
| 0.5         | Call        | ATM       | ~50%                        |
| 0.3         | Call        | OTM       | ~25%                        |
| 0.0         | Call        | Deep OTM  | ~0%                         |
| 0.0         | Put         | Deep OTM  | ~0%                         |
| -0.3        | Put         | OTM       | ~25%                        |
| -0.5        | Put         | ATM       | ~50%                        |
| -0.8        | Put         | ITM       | ~75%                        |
| -1.0        | Put         | Deep ITM  | ~100%                       |

## Gamma 
- Gamma represents the rate of change between an options delta and its underlying price. 
- Higher gammas indicate the option is more volatile
- This is called a second order price sensitivity. 
- Gamma indicates the amount the delta would change given a $1 change in the underlying asset
- Gamma is used to determine the stability of an option's delta
- Gamma is:
	- Higher for options that are ATM 
	- Lower for options that are OTM or ITM
	- Positive for long options
	- Negative for short options
	- Smaller the further away from the date of expiration (options with longer expirations are less sensitive to delta changes)

**Example:** 
Assume a stock has a delta of 0.4 and a gamma of 0.1. If the price of the stock increases or decreases by $1, then the option will increase or decrease in value by 40 cents and the delta will increase or decrease in value by 0.1. Now future moves will have a bigger impact due to the increased delta.

**Traders will use gamma to:**
- Decide to trade near vs long term
- Evaluate risks in option spreads
- Manage positions during volatile market periods

## Theta
- Measures the rate of time decay in an option or its premiums value
- The chance of an option being ITM decreases as time passes
- Time decay accelerates as the expiration date draws closer
- Theta is negative for long calls as options lose value due to time decay
- Theta is positive for short options
- Theta can be high for OTM otpions that have a lot of implied volatility
- Theta is typically highest for ATM options since less time is needed to earn a profit with a price move in the underlying asset
- Theta will increase sharply as time decay accelerates in the last few weeks before expiration
	- This can undermine a long option holders position especially if implied volatility declines simultanueously

**Example**:
If a stock has a theta value of 51.5 10 days before expiration, it indicates the option is losing $51.5 in value per day. 5 days later, the theta may have increased to $100, indicating the option is losing $100 in valuation each day. 

| Theta (per day) | Time to Expiration    | Moneyness            | Option Type | Time Decay         |
| --------------: | --------------------- | -------------------- | ----------- | ------------------ |
|  -0.05 to -0.15 | Near expiration       | ATM                  | Call/Put    | Fastest time decay |
|  -0.02 to -0.05 | Near expiration       | Slightly ITM/OTM     | Call/Put    | Rapid time decay   |
|  -0.01 to -0.02 | Moderate time         | ATM/Slightly ITM/OTM | Call/Put    | Steady time decay  |
| -0.005 to -0.01 | Moderate-to-long time | Moderately ITM/OTM   | Call/Put    | Slower time decay  |
|     0 to -0.005 | Far from expiration   | Deep ITM/OTM         | Call/Put    | Slowest time decay |
## Vega
- Measures the change in expected future volatility
- Higher volatility increaseses the chance that the option will hit the strike price at some point and therefore increases option price
- Given a change in implied volatility, vega shows how much an option price will increase or decrease
- Option sellers benefit from a fall in implied volatility, but the reverse is true for option buyers.
- When option prices are bid up because there are more buyers, implied volatility will increase.
- Long option traders benefit from pricing being bid up, and short option traders benefit from prices being bid down. This is why long options have a positive vega and short options have a negative vega.
- Vega can change without price changes of the underlying asset due to changes in implied volatility.
- Vega falls as the option approaches expiration.
- Traders can employ a [vega-neutral position](https://www.investopedia.com/terms/v/vega-neutral.asp) to offset the underlying asset's IV.