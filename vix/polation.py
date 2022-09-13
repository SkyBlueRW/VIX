"""
Interpolation
"""

from copy import deepcopy
import numpy as np 

from scipy.interpolate import pchip_interpolate, interp1d


def JiangTian_add_strike(strike_list, std, implied_forward):
    """
    Jiang & Tian (2005) Recommend to use Interpolation and Exterpolation to solve potential truncation errors and discretion errors. 
    In particular, they recommend to polate between -8 * std ~ 8 * std to reduce the truncation error. For each two strikes, the distance
    should be smaller than 0.35 * std to reduce the discretion error in the integration process.
    
    std is the un-annualized standard deviation


    """    
    strike_list = deepcopy(strike_list)

    # To obtain a robust integration as estimate, +- 8 * standard deviation of strikes is required
    lower_bound = np.exp(-8 * std) * implied_forward
    upper_bound = np.exp(8 * std) * implied_forward

    if lower_bound < min(strike_list):
        strike_list = [lower_bound] + strike_list 
    if upper_bound > max(strike_list):
        strike_list = strike_list + [upper_bound]

    # insert implied forward as a point
    if implied_forward not in strike_list:
        strike_list += [implied_forward]
    
    strike_list = sorted(strike_list)

    # Define max distance between any consecutive 2 strikes
    distance = 0.35 * std * implied_forward

    added_strike = []
    for i in range(len(strike_list) - 1):
        lin_num = int((strike_list[i+1] - strike_list[i]) // distance + 1)
        if lin_num > 1:
            new_strike = list(np.linspace(strike_list[i], strike_list[i+1], num=lin_num, endpoint=False)[1: ])
            added_strike += new_strike 
    
    res = strike_list + added_strike
    return sorted(res)
    

def interpolate(strike_list, implied_vol, new_strike_list):
    """
    Use Pchip (Piecewise Cubic Hermite Interpolating Polynomial) for interpolation
    Use flat line for expolation. The reason why a conventional linear polation is not used here is that it will frequently creat OTM option with a higher price thant ATM option
    To be noted that this method help to avoid arbitrage pattern at a cost of under-estimate VIX systematically
    """

    new_strike_list = sorted(new_strike_list)

    min_real_strike = min(strike_list)
    max_real_strike = max(strike_list)

    # pchip for interpolation
    interior_new_strike = [x for x in new_strike_list if (x>=min_real_strike) and (x<=max_real_strike)]
    interior_new_iv = pchip_interpolate(strike_list, implied_vol, interior_new_strike)
    interior_new_iv = list(interior_new_iv)

    # flat line for external polation
    new_implied_vol = [interior_new_iv[0]] * len([x for x in new_strike_list if x < min_real_strike]) + interior_new_iv + \
                    [interior_new_iv[-1]] * len([x for x in new_strike_list if x > max_real_strike])
    
    return new_implied_vol

    
    
def time_interpolation_linear(time_remaining, vix2, days=30):
    """
    Linear interpolation to convert to desired horizon
    """
    # Remove negative vix2 estimation
    time_remaining = [time_remaining[i] for i in range(len(vix2)) if vix2[i] > 0.]
    vix2 = [x for x in vix2 if x > 0.]

    # Do not interpolate when there is only 1 snapshot
    if len(vix2) == 1:
        vix = vix2[0]
    else:
        new_vix2 = interp1d(time_remaining, vix2, kind='linear', bounds_error=False, fill_value="extrapolate")
        vix = new_vix2(days) + 0.
    
    vix = 100 * np.sqrt(vix * 365 / days)

    return vix


