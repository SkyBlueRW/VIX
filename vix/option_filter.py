"""
期权筛选
"""

import numpy as np 


def filter_7d_option(option_data):
    """
    排除那些距离到期日不足7自然日的期权
    """
    return option_data.loc[option_data['remaining_time'] >= 7, :]


def filter_min_tick(option_data):
    """
    当期权价格小于最小的tick(0.0001)，认为由于rounding的原因存在较大的噪音，因此选择不用
    """
    return option_data.loc[option_data['price'] >= 0.0001, :]



def filter_upper_bound_lower_bound(option_data, implied_spot, t, r):
    """
    排除违反期权价值上下限的期权

    对于call，其范围应当是:
        max(implied_spot - dicount(strike), 0) ~ implied_spot
    对于put，其范围应当是:
        max(discount(strike) - implied_spot, 0) ~ discount(k)
    """

    def call_filter(price, s, k, t, r):
        """
        返回符合条件的call option filter
        """
        lower_bound = np.max([s - k / np.exp(r * t), 0])
        upper_bound = s

        if (lower_bound <= price <= upper_bound):
            return True 
        else:
            return False

    
    def put_filter(price, s, k, t, r):
        """
        返回符合条件的put option filter
        """
        lower_bound = np.max([k / np.exp(r * t) - s, 0]) 
        upper_bound = k / np.exp(r * t)

        if (lower_bound <= price <= upper_bound):
            return True 
        else:
            return False

    
    def option_filter(option_type, price, s, k, t, r):
        """
        """
        if option_type == 'call':
            return call_filter(price, s, k, t, r)
        else:
            return put_filter(price, s, k, t, r)

    
    filter_srs = option_data.apply(
        lambda x: option_filter(x.loc['option_type'], x.loc['price'], implied_spot, x.loc['strike'], t, r), raw=False, axis=1)
    
    return option_data.loc[filter_srs, :]
    

