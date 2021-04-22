"""
black-schole-merton 模型
"""

import numpy as np

from scipy import stats

def cal_option_price(s, k ,t, r, sigma, option_type):
    """
    计算bsm下欧式期权价格

    Parameters
    ----------
    option_type: str
        期权类型: call put
    """
    d1 = (np.log(s / k) + (r + 0.5 * sigma ** 2) * t)/(sigma * np.sqrt(t))
    d2 = (np.log(s / k) + (r - 0.5 * sigma ** 2) * t)/(sigma * np.sqrt(t))
    if option_type in ('call', 'c', 'C', 1):
        return s * stats.norm.cdf(d1, 0., 1.) - k * np.exp(-r * t ) * stats.norm.cdf(d2, 0., 1)
    elif option_type in ('put', 'p', 'P', -1):
        return -s * (1 - stats.norm.cdf(d1, 0., 1.)) + k * np.exp(-r * t) * (1 - stats.norm.cdf(d2, 0., 1))
    else:
        raise ValueError("只支持call 与 put")


def cal_implied_volatility(s, k, t, r, option_value, option_type, high=5., low=0.00001, maxiter=10000, tol=0.000001):
    """
    计算bsm下欧式期权隐含波动率

    Parameters
    ----------
    option_type: str
        期权类型: call put
    high: float
        隐含波动率最大可能值
    low: float
        隐含波动率最小可能只
    maxiter: int
        最大循环次数
    tol: float
        期权价格误差

    """
    # 阈值检查
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
