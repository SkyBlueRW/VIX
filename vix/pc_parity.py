"""
put call parity相关
"""

import numpy as np
import pandas as pd 

from .bsm import cal_implied_volatility

def cal_spot_ivforward(option_data, r, t):
    """
    给定相同到期日的期权合约数据，计算implied spot price 以及forward pair对应的 implied volatility

    参考 CBOE vix paper
    使用implied forward price用于判断期权是otm还是itm, 使用put call spread最小的strike计算implied forward price
    使用最小于implied forward price且最接近implied forward price的strike 作为atm strike

    """
    option_data = option_data.copy()

    # 生产期权价格table
    call = option_data.loc[option_data['option_type'] == 'call', ['strike', 'price']]
    put = option_data.loc[option_data['option_type'] == 'put', ['strike', 'price']]
    option_table = pd.merge(call, put, on=['strike'], how='outer', suffixes=['_call', '_put'])
    option_table['abs_dev'] = np.abs(option_table['price_call'] - option_table['price_put'])

    # 以 abs(call - put) 最小的strike，使用put call parity 计算implied forward
    forward_option_pair = option_table.iloc[option_table['abs_dev'].idxmin(), :]
    implied_forward = cal_implied_forward(forward_option_pair.loc['price_call'], forward_option_pair.loc['price_put'],
                                          forward_option_pair.loc['strike'], r, t)
    implied_spot = implied_forward / np.exp(r * t)

    # 计算这对pair对应的implied volatility
    iv_forward_pair = (cal_implied_volatility(implied_spot, forward_option_pair.loc['strike'], t, r, forward_option_pair.loc['price_call'], 'call') + 
                        cal_implied_volatility(implied_spot, forward_option_pair.loc['strike'], t, r, forward_option_pair.loc['price_put'], 'put')) / 2

    # # 找到 atm 对应的 strike
    # option_table = option_table.loc[option_table['strike'] <= implied_forward, :]
    # atm_strike = option_table.iloc[option_table['abs_dev'].idxmin(), :].loc['strike']

    return implied_spot, iv_forward_pair
 

def cal_implied_spot(c, p, k, r, t):
    """
    通过put call parity计算implied spot price
    """
    return c - p + k / np.exp(r * t)


def cal_implied_forward(c, p, k, r, t):
    """
    通过put call parity计算implied forward price
    """
    return (c - p) * np.exp(r * t) + k
