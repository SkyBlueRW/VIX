# Vix
For Vix calculation (volatility index)
# VIX Calculation

**An introduction on VIX**

VIX index is the market expectation of future realized volatility under risk neutral measure (Or more appropriately it is the quadratic variation instead of realized volatility). We will be able to construct the VIX index as a replicating portfolio of variance futures so that vix index and option premium (replicating cost) can be linked. Thus a model free estimation of vix is here. 


**Information Content of VIX**

Conventially, VIX index is taken as a good estimator of realized volatility for a future period. Jiang & Tian (2005) argued that the model free VIX index contains historical realized volatility. In a regression analysis of future realized volatility ~ VIX index + historical realized volatility, VIX index is siginificant while the coefficient is not 1 (They argued that this is a demonstration that VIX is a biased estimator on future realized volatility - usually higher than 1 a phenomenon related to variance risk premium). They concluded that the model free vix contains the information of historical realized volatility and is an more efficient estimator on future realized volatility.

As Jiang & Tian (2005) demonstrated, VIX is usually larger than future realized volatility. This phenomenon is in some degree related to variance risk premium (VRP - the strike price of US variance swap is usually larger than realized variance). Carr & Wu (2008) believes that the difference between VIX and future realized variance can be used as an estimator of VRP. They argued that "investors are willing to pay extra money to enter into variance because they dislike variance, not just because it is anti-correlated with stock prices, but on its own right. This lead to many considerating variance as an asset clas in and of itself"





