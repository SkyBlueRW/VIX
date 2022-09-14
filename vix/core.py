"""
Core calculation for vix
"""
import numpy as np 

from . import bsm, integration, option_filter, pc_parity, polation 


def cal_vix(data, r, horizon=30):
    """
    calculate the volatility expectation of a specified horizon (Under CBOE setting the horizon is 30 natural day)

    Adjustment on the COBE method:
        # 1. Interpolate strikes according to Jiang & Tian (2005)
        # 2. Chip integration instead of rectangle integration. It is more robust to some weired vol shape
        # 3. Interpolate to reduce discretion errror
        # 4. Extopolate to reduce the trunction error

    Parameters
    ----------
    data: pd.DataFrame
        Required data field: option_type, strike, price, time_remaining
        I.E:
            option_type,  strike,  price,  time_remaining
            'put'           2.3     0.15       30
            'put'           2.3     0.21       60
            'call'          2.3     0.15       30
            'call'          2.3     0.23       60
    
    r: float
        annualized risk free rate
    horizon: int
        horizon of future period, in natural days
    
    Returns
    -------
        100 * expected vol
    """

    # Only use options with days to maturity (natural day) > 7
    # Option near to maturity often exhibit weird volatility level 
    # One example would be that since the decay of option premium speed up as maturity approach, investors tend to sell theses options for a sell vol strategy
    # Another example would be that investors are unwilling to take over night risk and hence impact the curve
    data = data.loc[data['time_remaining'] >= 7, :].copy()


    # Remove potential duplicates due to dividend split. Chose the one with largets volume, amount or OI
    label = [x for x in ('amount', 'volume', 'oi') if x in data.columns]
    if len(label) > 0:
        data = data.sort_values(by=['time_remaining', 'option_type', 'strike', label[0]], ascending=True)
    data = data.drop_duplicates(subset=['time_remaining', 'option_type', 'strike'], keep='last').loc[:, ['option_type', 'strike', 'price', 'time_remaining']]

    # snapshot for estimation
    maturity_list = sorted(data['time_remaining'].unique())

    assert min(maturity_list) < horizon * 2, "near term maturity to date is {}".format(min(maturity_list))

    # Calculate VIX^2 (not annualized) for each snapshot
    vix2 = []
    for x in maturity_list:
        try:
            tmp = single_maturity_vix2(data.loc[data['time_remaining'] == x, :], x / 365, r)
        except Exception as e:
            vix2.append(np.nan)
        else:
            vix2.append(tmp)
 
    # use linear interpolation for the specified horizon of vix (30 for CBOE)
    vix = polation.time_interpolation_linear(maturity_list, vix2, days=horizon)


    return vix


def single_maturity_vix2(option_data, t, r):
    """
    """
    option_data = option_data.sort_values(by=['option_type', 'strike'], ascending=[True, True])[['strike', 'price', 'option_type']]

    # Calculate implied spot and atm vol
    implied_spot, iv_forward_pair = pc_parity.cal_spot_ivforward(option_data, r, t)
    implied_forward = implied_spot * np.exp(r * t)

    # Calculate implied vol for all options
    option_data['implied_vol'] = option_data.apply(
        lambda x: bsm.cal_implied_volatility(implied_spot, x.loc['strike'], t, r, x.loc['price'], x.loc['option_type']),
        raw=False, axis=1
    )


    # Remove options with large noice
    # those violate arbitrage free assumption
    # those premium less than a tick
    option_data = option_filter.filter_upper_bound_lower_bound(option_data, implied_spot, t, r)
    option_data = option_filter.filter_min_tick(option_data)


    # calculate underlying atm std
    opt_std = iv_forward_pair * np.sqrt(t)

    call_data = option_data.loc[option_data['option_type'] == 'call', ['strike', 'price', 'implied_vol']]
    put_data = option_data.loc[option_data['option_type'] == 'put', ['strike', 'price', 'implied_vol']]
    call_data = call_data.sort_values(by=['strike'], ascending=True)
    put_data = put_data.sort_values(by=['strike'], ascending=True)


    # Determine the strike range to polation according to Jiang & Tian (2005)
    # +- 8 * opt standard deviation as range
    # 0.35 * opt standard deviation should be the maximum distance between any strike
    call_strike = polation.JiangTian_add_strike(call_data['strike'].tolist(), opt_std, implied_forward)
    put_strike = polation.JiangTian_add_strike(put_data['strike'].tolist(), opt_std, implied_forward)


    # Polation. Chip interoplation and flat line exterpolation
    call_iv = polation.interpolate(call_data['strike'].tolist(), call_data['implied_vol'].tolist(), call_strike)
    put_iv = polation.interpolate(put_data['strike'].tolist(), put_data['implied_vol'].tolist(), put_strike)


    # Calculate BSM price for the final integration of vix2
    call_price = [bsm.cal_option_price(implied_spot, call_strike[i], t, r, call_iv[i], 'call') for i in range(len(call_strike))]
    put_price = [bsm.cal_option_price(implied_spot, put_strike[i], t, r, put_iv[i], 'put') for i in range(len(put_strike))]

    # Trapz integration for the vix^2 of a signle snapshot
    vix2 = integration.trapz(call_strike, call_price, put_strike, put_price, implied_forward, r, t)

    return vix2



