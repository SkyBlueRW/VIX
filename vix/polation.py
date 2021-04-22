"""
strike 内插值
"""

from copy import deepcopy
import numpy as np 

from scipy.interpolate import pchip_interpolate, interp1d


def JiangTian_add_strike(strike_list, std, implied_forward):
    """
    Reference: Jiang & Tian (2005)
    
    确定需要插值的strike位置
    范围为 -8 * std ~ * std 用于解决积分中存在的truncation error
    两个strike之间相距应小于 0.35 * std 用于解决积分汇总存在的discretion error

    注: std为非年化的标准差

    """    
    strike_list = deepcopy(strike_list)

    # 需要8倍标准差的strike 宽度来获得稳健的积分估计, 如果并不足够，则补齐连孤单
    lower_bound = np.exp(-8 * std) * implied_forward
    upper_bound = np.exp(8 * std) * implied_forward

    if lower_bound < min(strike_list):
        strike_list = [lower_bound] + strike_list 
    if upper_bound > max(strike_list):
        strike_list = strike_list + [upper_bound]

    # 将implied_forward 插入
    if implied_forward not in strike_list:
        strike_list += [implied_forward]
    
    strike_list = sorted(strike_list)

    # 内插使得间距不大于0.35sd
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
    内插使用 pchip(Piecewise Cubic Hermite Interpolating Polynomial)
    外插使用 平插， 原因在于，如果使用linear的方式进行插值，经常会出现otm 价格高于 atm价格的violation。
    因此为了保持一致性，使用平行插值，需要注意的是，在市场大涨大跌时，这种插值方法会出现一定程度上的低估的问题
    """

    new_strike_list = sorted(new_strike_list)

    min_real_strike = min(strike_list)
    max_real_strike = max(strike_list)

    # 内部使用pchip的方式进行内插
    interior_new_strike = [x for x in new_strike_list if (x>=min_real_strike) and (x<=max_real_strike)]
    interior_new_iv = pchip_interpolate(strike_list, implied_vol, interior_new_strike)
    interior_new_iv = list(interior_new_iv)

    # 外部使用平插
    new_implied_vol = [interior_new_iv[0]] * len([x for x in new_strike_list if x < min_real_strike]) + interior_new_iv + \
                    [interior_new_iv[-1]] * len([x for x in new_strike_list if x > max_real_strike])
    
    return new_implied_vol

    
    
def time_interpolation_linear(time_remaining, vix2, days=30):
    """
    通过内插值获得对应horizon的vix
    """
    # 排除vix2为负的（错误计算）
    time_remaining = [time_remaining[i] for i in range(len(vix2)) if vix2[i] > 0.]
    vix2 = [x for x in vix2 if x > 0.]

    # 若只有1个值，则选用该值不进行插值
    if len(vix2) == 1:
        vix = vix2[0]
    else:
        new_vix2 = interp1d(time_remaining, vix2, kind='linear', bounds_error=False, fill_value="extrapolate")
        vix = new_vix2(days) + 0.
    
    vix = 100 * np.sqrt(vix * 365 / days)

    return vix


