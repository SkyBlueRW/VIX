"""

calculate single period volatility expectation via integration
"""

import numpy as np 


def trapz(call_strike, call_price, put_strike, put_price, atm_price, r, t):
    """
    trapezodial integration integration. Similar to what is adopted in CBOE method.
    Used for the integration of one single volatility at one horizon
    """

    # Select only OTM for better liquidity
    call_price = [call_price[i] for i in range(len(call_strike)) if call_strike[i] >= atm_price]
    put_price = [put_price[i] for i in range(len(put_strike)) if put_strike[i] <= atm_price]

    call_strike = [x for x in call_strike if x >= atm_price]
    put_strike = [x for x in put_strike if x <= atm_price]

    # merge both put and call
    option_price = put_price + call_price 
    strike = put_strike + call_strike 
    
    # price / k^2
    option_price_k2 = [option_price[i] / strike[i] ** 2 for i in range(len(option_price))] 

    # integration
    vix2 = 2 * np.exp(r * t) * np.trapz(option_price_k2, strike)

    return vix2

