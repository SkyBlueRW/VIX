"""
Option filter
"""

import numpy as np 


def filter_7d_option(option_data):
    """
    Remove options with days to maturity < 7
    """
    return option_data.loc[option_data['remaining_time'] >= 7, :]


def filter_min_tick(option_data):
    """
    Remove options with premium smaller than a tick (0.0001). 
    Usually there is large noice in such options due to rounding issues
    """
    return option_data.loc[option_data['price'] >= 0.0001, :]



def filter_upper_bound_lower_bound(option_data, implied_spot, t, r):
    """
    Remove options that violate the No-arbitrage assumption

    For Call option, premium should be within
        max(implied spot - discount(strike), 0) ~ implied spot
    For Put option, premium should be within
        max(discount(strike) - implied spot, 0) ~ discount(k)

    """

    def call_filter(price, s, k, t, r):
        lower_bound = np.max([s - k / np.exp(r * t), 0])
        upper_bound = s

        if (lower_bound <= price <= upper_bound):
            return True 
        else:
            return False

    
    def put_filter(price, s, k, t, r):
        lower_bound = np.max([k / np.exp(r * t) - s, 0]) 
        upper_bound = k / np.exp(r * t)

        if (lower_bound <= price <= upper_bound):
            return True 
        else:
            return False

    
    def option_filter(option_type, price, s, k, t, r):
        if option_type == 'call':
            return call_filter(price, s, k, t, r)
        else:
            return put_filter(price, s, k, t, r)

    
    filter_srs = option_data.apply(
        lambda x: option_filter(x.loc['option_type'], x.loc['price'], implied_spot, x.loc['strike'], t, r), raw=False, axis=1)
    
    return option_data.loc[filter_srs, :]
    

