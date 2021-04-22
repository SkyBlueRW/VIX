"""
通过积分的方式计算vix
"""

import numpy as np 


def trapz(call_strike, call_price, put_strike, put_price, atm_price, r, t):
    """
    类似CBOE的方法通过trapezodial integration的方式利用期权价格估计单一周期vix
    """

    # 选择otm的部分(流动性更好)
    call_price = [call_price[i] for i in range(len(call_strike)) if call_strike[i] >= atm_price]
    put_price = [put_price[i] for i in range(len(put_strike)) if put_strike[i] <= atm_price]

    call_strike = [x for x in call_strike if x >= atm_price]
    put_strike = [x for x in put_strike if x <= atm_price]

    # 合并
    option_price = put_price + call_price 
    strike = put_strike + call_strike 
    
    # price / k^2
    option_price_k2 = [option_price[i] / strike[i] ** 2 for i in range(len(option_price))] 

    # 单一周期vix
    vix2 = 2 * np.exp(r * t) * np.trapz(option_price_k2, strike)

    return vix2

