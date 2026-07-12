- First widely used mathematical method to calculate theoretical value of an option contract

**Assumptions**:
- Instruments such as stock shares or futures contracts will have a [[Glossary#Lognormal|lognormal distribution]] of prices following a random walk with constant drift and volatility.
- No dividends are paid out during the life of the option.
- Markets are random because market movements can't be predicted.
- There are no transaction costs when buying the option.
- The risk-free rate and volatility of the underlying asset are known and constant.
- The returns of the underlying asset are normally distributed.
- The option is European and can only be exercised at expiration.

**Variables:** 
- $C =$ Call option price 
- $S =$ Current stock price
- $K =$ Strike price
- $r=$ Risk-free interest rate
- $t=$ Time until expiration date
- $N=$ Cumulative distribution function for a standard normal distribution
- $\sigma_X =$ Standard deviation of random variable $X$

# Formula
$$C=SN(d_1)-Ke^{-rt}N(d_2)$$
Where:$$d_1 = \frac{\ln\frac S K +(r+\frac{\sigma_v^2}{2})t}{\sigma_s\sqrt t}$$And:$$
d_2=d_1-\sigma_s\sqrt t=\frac{\ln\frac S K +(r-\frac{\sigma_v^2}{2})t}{\sigma_s\sqrt t}$$
# Intuition:
- $N(d)$ is roughly the probability we are going to do the action associated with the term
- The value of the call option is the value of the stock minus the strike price discounted back to the current day (European so can only be exercised at expiration)
- The first term is how much you stand to earn:
	- Ie: the current stock price weighted by the probability that you "get" it
- The second term is how much you pay
	- Ie: The strike price discounted to today minus the probability you pay it
- The higher the stock price relative to the exercise price:
	- The more the option is worth
	- The more likely you are to exercise the option
	- The higher $\frac S K \implies$ The higher $d_1$ and $d_2 \implies$ The higher $N(d_i)$
- The higher the [[Glossary#Volatility|volatility]]:
	- The higher the option price (as the peaks are greater)
	- The higher the standard deviation
	- $d_1$ increases while $d_2$ decreases with standard deviation, increasing the first term and decreasing the second, thus increasing C
