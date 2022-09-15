# Vix
For Vix calculation (volatility index)

## Intro

**An introduction on VIX**

VIX index is the market expectation of future realized volatility under risk neutral measure (Or more appropriately it is the quadratic variation instead of realized volatility). We will be able to construct the VIX index as a replicating portfolio of variance futures so that vix index and option premium (replicating cost) can be linked. Thus a model free estimation of vix is here. 


**Information Content of VIX**

Conventially, VIX index is taken as a good estimator of realized volatility for a future period. Jiang & Tian (2005) argued that the model free VIX index contains historical realized volatility. In a regression analysis of future realized volatility ~ VIX index + historical realized volatility, VIX index is siginificant while the coefficient is not 1 (They argued that this is a demonstration that VIX is a biased estimator on future realized volatility - usually higher than 1 a phenomenon related to variance risk premium). They concluded that the model free vix contains the information of historical realized volatility and is an more efficient estimator on future realized volatility.

As Jiang & Tian (2005) demonstrated, VIX is usually larger than future realized volatility. This phenomenon is in some degree related to variance risk premium (VRP - the strike price of US variance swap is usually larger than realized variance). Carr & Wu (2008) believes that the difference between VIX and future realized variance can be used as an estimator of VRP. They argued that "investors are willing to pay extra money to enter into variance because they dislike variance, not just because it is anti-correlated with stock prices, but on its own right. This lead to many considerating variance as an asset clas in and of itself"


## Intuition of VIX index
**Replicating**

$$\frac{dS_t}{S_t} = \mu(t,...)dt + \sigma(t,...)dZ_t$$

$$
\begin{aligned}
F &= E^Q[e^{-rT}(V - K)]
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