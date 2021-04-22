"""
计算vix
"""
import numpy as np 

from . import bsm, integration, option_filter, pc_parity, polation 


def cal_vix(data, r, horizon=30):
    """
    计算指定horizon波动率在风险中性测度下的期望值(vix是horizon=30)

    Parameters
    ----------
    data: pd.DataFrame
        至少要包括option_type, strike, price, time_remaining(自然日)
        I.E:
            option_type,  strike,  price,  time_remaining
            'put'           2.3     0.15       30
            'put'           2.3     0.21       60
            'call'          2.3     0.15       30
            'call'          2.3     0.23       60
    
    r: float
        年华的无风险收益率
    horizon: int
        波动率周期
    
    Returns
    -------
        100 * expected vol
    """
    # 只使用剩余时间(自然日)超过7天的期权。
    # 即将到期的期权经常由于交易行为呈现出特殊的波动率水平与结构 
    # 比如，由于期权价格衰减随时间加速，会有投资者倾向于只卖快到期的期权 
    # 又比如，由于投资者不愿意行权承担隔夜风险，期权价格会常常出现套利机会(时间价值为负等)
    data = data.loc[data['time_remaining'] >= 7, :].copy()

    # 去重,由于分红调整的原因。会出现同一到期日，同样strike的期权在交易。此时选择成交量或者成交额更大的那个保留
    # 若没有volume, amount, oi等各类数据，则随机去除一个
    label = [x for x in ('amount', 'volume', 'oi') if x in data.columns]
    if len(label) > 0:
        data = data.sort_values(by=['time_remaining', 'option_type', 'strike', label[0]], ascending=True)
    data = data.drop_duplicates(subset=['time_remaining', 'option_type', 'strike'], keep='last').loc[:, ['option_type', 'strike', 'price', 'time_remaining']]

    # 不同到期日的期权
    maturity_list = sorted(data['time_remaining'].unique())

    assert min(maturity_list) < horizon * 2, "near term期权到期日为{}".format(min(maturity_list))

    # 对于每一个到期日，利用对应的期权计算vix^2 (未年化)
    # 相比CBOE的改进
    # 1. 使用Jiang & Tian (2005)的方法确定需要插值的strike
    # 2. 使用cubic (Piecewise Cubic Hermite Interpolating Polynomial)的插值方法对期权隐含波动率进行内插。这一步是为了解决discretion error
    #    根据Jiang & Tian (2008)的描述，两个strike之间的距离应当小于0.35 * vol。此时的discretion error可忽略不计
    # 3. 使用平插值的方法对外部进行插值。美国市场以及 Jiang & Tian (2008)大部分都使用线性插值的方法。但是由于国内的strike过于稀少，这种方法在国内并不适用(可能导致otm价格高于atm价格)
    #    平插值方法会在市场剧烈波动，一侧strike数量极少时低估波动率，不过这种低估并不显著。外插是为了解决trunction error的问题。通常 8 * std下的trunction error可以忽略不计
    # 4. 使用了梯形积分而不是矩形积分。在某些波动率曲面非常怪异的情况下会比较稳健。
    vix2 = []
    for x in maturity_list:
        try:
            tmp = single_maturity_vix2(data.loc[data['time_remaining'] == x, :], x / 365, r)
        except Exception as e:
            vix2.append(np.nan)
        else:
            vix2.append(tmp)
    # print(vix2)
    # 使用线性插值的方法，利用不同到期日下的vix2计算指定horizon(CBOE是30)的vix
    vix = polation.time_interpolation_linear(maturity_list, vix2, days=horizon)


    return vix


def single_maturity_vix2(option_data, t, r):
    """
    option_data需要包括 strike, price, option_type
    """
    option_data = option_data.sort_values(by=['option_type', 'strike'], ascending=[True, True])[['strike', 'price', 'option_type']]

    # 计算implied spot与atm vol
    implied_spot, iv_forward_pair = pc_parity.cal_spot_ivforward(option_data, r, t)
    implied_forward = implied_spot * np.exp(r * t)

    # 为所有期权计算隐含波动率
    option_data['implied_vol'] = option_data.apply(
        lambda x: bsm.cal_implied_volatility(implied_spot, x.loc['strike'], t, r, x.loc['price'], x.loc['option_type']),
        raw=False, axis=1
    )

    # 进行filter
    # 排除超出upper / lower bound的期权
    # 排除价格低于1tick(0.0001)的期权
    option_data = option_filter.filter_upper_bound_lower_bound(option_data, implied_spot, t, r)
    option_data = option_filter.filter_min_tick(option_data)


    # 计算underlying atm std
    opt_std = iv_forward_pair * np.sqrt(t)

    call_data = option_data.loc[option_data['option_type'] == 'call', ['strike', 'price', 'implied_vol']]
    put_data = option_data.loc[option_data['option_type'] == 'put', ['strike', 'price', 'implied_vol']]
    call_data = call_data.sort_values(by=['strike'], ascending=True)
    put_data = put_data.sort_values(by=['strike'], ascending=True)

    # 借助Jiang & Tian (2005)确定需要插值的strike的密度
    # 外部应当在 +- 8 opt_std
    # 内部任意两个strike之间的距离应当小于0.35 opt_std 
    call_strike = polation.JiangTian_add_strike(call_data['strike'].tolist(), opt_std, implied_forward)
    put_strike = polation.JiangTian_add_strike(put_data['strike'].tolist(), opt_std, implied_forward)

    # print(call_data['strike'].tolist())
    # print(opt_std)
    # print(implied_forward)


    # 进行插值，内部使用cubic插值，外部使用平插
    call_iv = polation.interpolate(call_data['strike'].tolist(), call_data['implied_vol'].tolist(), call_strike)
    put_iv = polation.interpolate(put_data['strike'].tolist(), put_data['implied_vol'].tolist(), put_strike)


    # 对于插值出来的iv，计算其价格用于vix2计算
    call_price = [bsm.cal_option_price(implied_spot, call_strike[i], t, r, call_iv[i], 'call') for i in range(len(call_strike))]
    put_price = [bsm.cal_option_price(implied_spot, put_strike[i], t, r, put_iv[i], 'put') for i in range(len(put_strike))]

    # 使用trapz积分估计单一到期日期权的vix^2
    vix2 = integration.trapz(call_strike, call_price, put_strike, put_price, implied_forward, r, t)

    return vix2



