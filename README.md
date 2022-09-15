# Vix
For Vix calculation (volatility index)

## Intro

**An introduction on VIX**

VIX index is the market expectation of future realized volatility under risk neutral measure (Or more appropriately it is the quadratic variation instead of realized volatility). We will be able to construct the VIX index as a replicating portfolio of variance futures so that vix index and option premium (replicating cost) can be linked. Thus a model free estimation of vix is here. 


**Information Content of VIX**

Conventially, VIX index is taken as a good estimator of realized volatility for a future period. Jiang & Tian (2005) argued that the model free VIX index contains historical realized volatility. In a regression analysis of future realized volatility ~ VIX index + historical realized volatility, VIX index is siginificant while the coefficient is not 1 (They argued that this is a demonstration that VIX is a biased estimator on future realized volatility - usually higher than 1 a phenomenon related to variance risk premium). They concluded that the model free vix contains the information of historical realized volatility and is an more efficient estimator on future realized volatility.

As Jiang & Tian (2005) demonstrated, VIX is usually larger than future realized volatility. This phenomenon is in some degree related to variance risk premium (VRP - the strike price of US variance swap is usually larger than realized variance). Carr & Wu (2008) believes that the difference between VIX and future realized variance can be used as an estimator of VRP. They argued that "investors are willing to pay extra money to enter into variance because they dislike variance, not just because it is anti-correlated with stock prices, but on its own right. This lead to many considerating variance as an asset clas in and of itself"


## Intuition of VIX index


Assume market price of the underlying follows the Geometric Brownian Motion without jump as below.

$$\frac{dS_t}{S_t} = \mu(t,...)dt + \sigma(t,...)dZ_t$$


**Variance Forward**

For a variance forward with delievery price of k, its price should be $F = E^Q[e^{-rT}(V - K)]$ as per no arbitrage pricing where V is the realized variance $V = \frac{1}{T}\int_o^T\sigma^2(t,...)dt$.

For such a forward, the fair delivery price (the delievery price k that set F to 0) should be as follows 

$$
\begin{aligned}
K_{var} &= E^Q[V] \\
&=\frac{1}{T}E^Q[\int_o^T\sigma^2(t,...)dt]
\end{aligned}
$$

**Replicating variance forward**
Since the instantaneous variance is unknown, we hope to construct a replicating portfolio to estimate $K_{var}$

$$
\begin{aligned}
K_{var} &= \frac{1}{T}E^Q[\int_o^T\sigma^2(t,...)dt] \\
&= \frac{2}{T} E^Q[\int_0^T \frac{dS_t}{S_t} - d(logS_t)] \\ 
& =  \frac{2}{T} E^Q[\int_0^T\frac{dS_t}{S_t} - log(\frac{S_T}{S_0})]
\end{aligned}
$$

It is clear that, exposue to variance can be obtained via 2 positions:

1. a dynamic position on $\frac{1}{S_t}$ share of the underlying
2. a static position on log contract

Based on the assumption, we can get the expectation of part 1 as $E^Q[\int_0^T \frac{dS_t}{S_t}] = rT$

As to part 2 (the static log contract), we can obtain the log contract via the portfolio of forward and options. 

$$
\begin{aligned}
\frac{S_T}{S_0} &= log\frac{S_T}{S_{\star}} + log\frac{S_{\star}}{S_0} \\ 
log\frac{S_T}{S_{\star}} & = \frac{S_T - S_{\star}}{S_{\star}} \\
&+\int_0^{S_\star} \frac{1}{k^2} Max(K-S_T, 0)dK \\
&+\int_{S_\star}^{\infty} \frac{1}{k^2} Max(S_T - K, 0)dK
\end{aligned}
$$



**Legacy CBOE VIX calculation**

The initial version of the CBOE VIX index is based on Whaley(1993, 2000). The method at the time is based on S&P 100 indx options. It take the equal weighted average of the Implied volatility of ATM option as the VIX Index. 

There are 2 major drawbacks on this method. Firstly, it relies on BSM model to get implied volatility hence it is susceptibel to BSM errors. Secondly it might ignore information from OTM and ITM options.

Since 2003, COBE improved their method based on DDKZ (1999) reserach report and change the underlying to S&P 500. It is the current version of method that CBOE used for VIX index calculation.

## Reference
- DDKZ(1999): More Than You Ever Wanted to Know About Volatility Swaps
- CBOE vix white paper
- Jiang & Tian (2005): The Model-Free Implied Volatility and Its Information Cotent
- Jiang & Tian (2009): Extracting Model-Free Volatility from Option Prices: An Examination of the VIX Index
- Carr & Wu (2008): Variance Risk Premium


## Usage Demo

```python 
from vix import cal_vix

# Fetch data 
option_data = get_option_data('YYYY-MM-dd')
risk_free_rate = get_risk_free_rate('YYYY-MM-dd')

# Calculate
vix = cal_vix(option_data, risk_free_rate, horizon=30)
```

**Data Input Example**
1. required data field for option_data：option_type, strike, price, time_remaining(natural day)

    I.E:
            option_type,  strike,  price,  time_remaining
            'put'           2.3     0.15       30
            'put'           2.3     0.21       60
            'call'          2.3     0.15       30
            'call'          2.3     0.23       60

2. risk_free_rate: should be after annualzation