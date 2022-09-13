"""
black-schole-merton Model
"""

import numpy as np

from scipy import stats

def cal_option_price(s, k ,t, r, sigma, option_type):
    """
    Calculate Premium for European Option

    Parameters
    ----------
    s: float
        Spot price
    k: float
        Strike price
    t: float
        Time to maturity in unit
    sigma: float
        Volatility
    option_type: str
        Option type: call put
    
    Return
    ------
    Option Premium

    """
    d1 = (np.log(s / k) + (r + 0.5 * sigma ** 2) * t)/(sigma * np.sqrt(t))
    d2 = (np.log(s / k) + (r - 0.5 * sigma ** 2) * t)/(sigma * np.sqrt(t))
    if option_type in ('call', 'c', 'C', 1):
        return s * stats.norm.cdf(d1, 0., 1.) - k * np.exp(-r * t ) * stats.norm.cdf(d2, 0., 1)
    elif option_type in ('put', 'p', 'P', -1):
        return -s * (1 - stats.norm.cdf(d1, 0., 1.)) + k * np.exp(-r * t) * (1 - stats.norm.cdf(d2, 0., 1))
    else:
        raise ValueError("Only Support call and put")


def cal_implied_volatility(s, k, t, r, option_value, option_type, high=5., low=0.00001, maxiter=10000, tol=0.000001):
    """
    Calculate Implied volatility for European Option with BSM model
    
    Bisection search is used to solve the equation

    Parameters
    ----------
    option_type: str
        Option Type: call put
    high: float
        Max possible implied volatility
    low: float
        Min possible implied volatility
    maxiter: int
        Max Iteration Number
    tol: float
        Tolerance of Diff in Option price

    Returns
    -------
    Implied volatility

    """
    # check outlier
    upper_bound = cal_option_price(s, k, t, r, high, option_type)
    lower_bound = cal_option_price(s, k, t, r, low, option_type)
    if not (lower_bound <= option_value <= upper_bound):
        return np.nan

    for i in range(maxiter):
        mid = (high + low) / 2
        if mid < 0.00001:
            mid = 0.00001
        estimate = cal_option_price(s, k, t, r, mid, option_type)
        if abs(estimate - option_value) < tol:
            break
        elif estimate > option_value:
            high = mid
        elif estimate < option_value:
            low = mid
    if abs(estimate - option_value) < tol:
        return mid
    else:
        return np.nan
