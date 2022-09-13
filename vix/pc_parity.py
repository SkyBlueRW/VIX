"""
put call parity相关

"""

import numpy as np
import pandas as pd 

from .bsm import cal_implied_volatility

def cal_spot_ivforward(option_data, r, t):
    """

    Given a snapshot of all option, calculate the implied spot price, and implied volatility for the ATM option (call and put)

    Ref: CBOE vix paper
        Use implied forward price to determin whether an option is OTM or ITM. 
        Use the strike with minimum put call spraed to calculate implied forward price
        Use the strike that is smaller than impled forward price and closest implied forward price as ATM strike

    """
    option_data = option_data.copy()

    # Generate Option price Table
    call = option_data.loc[option_data['option_type'] == 'call', ['strike', 'price']]
    put = option_data.loc[option_data['option_type'] == 'put', ['strike', 'price']]
    option_table = pd.merge(call, put, on=['strike'], how='outer', suffixes=['_call', '_put'])
    option_table['abs_dev'] = np.abs(option_table['price_call'] - option_table['price_put'])

    # Take the stike with minimum abs(call - put) as ATM. Calculate Put-Call pairity implied forward price
    forward_option_pair = option_table.iloc[option_table['abs_dev'].idxmin(), :]
    implied_forward = cal_implied_forward(forward_option_pair.loc['price_call'], forward_option_pair.loc['price_put'],
                                          forward_option_pair.loc['strike'], r, t)
    implied_spot = implied_forward / np.exp(r * t)

    # Calculate implied volatility for the pair of ATM options
    iv_forward_pair = (cal_implied_volatility(implied_spot, forward_option_pair.loc['strike'], t, r, forward_option_pair.loc['price_call'], 'call') + 
                        cal_implied_volatility(implied_spot, forward_option_pair.loc['strike'], t, r, forward_option_pair.loc['price_put'], 'put')) / 2

    # option_table = option_table.loc[option_table['strike'] <= implied_forward, :]
    # atm_strike = option_table.iloc[option_table['abs_dev'].idxmin(), :].loc['strike']

    return implied_spot, iv_forward_pair
 

def cal_implied_spot(c, p, k, r, t):
    """
    Calculate implied spot price via put-call parity
    """
    return c - p + k / np.exp(r * t)


def cal_implied_forward(c, p, k, r, t):
    """
    Calculate implied forward price via put-call parity
    """
    return (c - p) * np.exp(r * t) + k
