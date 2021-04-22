# Vix
For Vix calculation (volatility index)
# VIX 计算

**vix介绍**
vix是市场对于未来实现波动率(更确切说应当是quadratic variation)在风险中性测度下的期望。若市场上存在variance swap(或期货)，则通过对于这个衍生品的定价可以得到vix，cboe的方法在于利用期货与一系列期权的组合来replicate variance swap，从而将vix与期权价格(replicating cost)联系了起来。而得到了一个model free的vix估计方法(不依特定赖于期权定价模型)

**信息含量**
通常认为vix是对未来一段时间realized volatility的一个很好的估计，Jiang & Tian(2005)的文章认为model free的vix包含了历史realized volatility。在使用未来realized volatility作为因变量，使用model free vix 与历史realized volatility作为自变量的回归中，model free vix的系数显著，但不为1(他们认为这代表vix是biased的估计)，而realized
volatility的系数不再显著。因此他们得到结论model free vix包含了历史realized volatility的信息并且是比历史realized volatility更efficient的估计。

如Jiang & Tian(2005)在文章中所述，vix通常是大于未来realized volatility的。这个现象与variance risk premium (VRP)相关，所谓VRP是指美国variance swap市场中strike 通常是大于realized variance的现象。由于vix本身对应的是strike，因此反应在vix上会有相同的现象。Carr & Wu使用vix与未来实现波动率的差值作为VRP的估计并认为"investors are willing to pay extra money to enter into variance because they dislike variance, not just because it is anti-correlated with stock prices, but on its own right. This leads to many considering variance as an asset class in and of itself"

## 使用说明
```python 
from vix import cal_vix

# 自行获取数据
option_data = get_option_data('YYYY-MM-dd')
risk_free_rate = get_risk_free_rate('YYYY-MM-dd')

# 进行计算
vix = cal_vix(option_data, risk_free_rate, horizon=30)
```

**数据格式**
1. option_data至少应当包含字段：option_type, strike, price, time_remaining(自然日)
    I.E:
            option_type,  strike,  price,  time_remaining
            'put'           2.3     0.15       30
            'put'           2.3     0.21       60
            'call'          2.3     0.15       30
            'call'          2.3     0.23       60

2. option_data中同样可以提供amount, volume, oi字段，这些字段可以用于出现相同到期日，行权价的期权时，用于鉴别选择某个期权的价格进行计算

3. risk_free_rate 应当是年化后的值


**计算逻辑**
    1. 使用put call spread最小的那一对put call 期权通过put call parity的形式计算implied forward price。并使用这个implied forward price计算bsm隐含波动率作为ATM的隐含波动率
    $$
    F_0 = e^{rT}(C - p) + K
    $$
    2. 进行期权筛选，分别删去以下3种期权
        - 到期时间少于7个自然日
        - 期权价格小于最小tick(0.0001)
        - 违反期权upper bound 与lower bound(使用implied forward price计算)
    3. 如果由于分红的情况，出现2个有相同到期日与strike的期权，则使用成交额更大的那个期权，删去成交额/成交量/oi更小的那一个
    4. 使用下述提供的方法，确定需要进行插值的fake strike并对这些fake strike对应的隐含波动率进行插值。
    5. 根据插值得到的隐含波动率，计算这些fake strike对应的期权的bsm期权价格。
    6. 借助Demeterfi e al (1999)给出的等价形式，通过梯形积分，估计各个到期日的期权对应的波动率
    7. 使用线性插值计算对应周期为30天的年化的vix

## vix背景相关

**Reference**
- DDKZ(1999): More Than You Ever Wanted to Know About Volatility Swaps
- CBOE vix white paper
- Jiang & Tian (2005): The Model-Free Implied Volatility and Its Information Cotent
- Jiang & Tian (2009): Extracting Model-Free Volatility from Option Prices: An Examination of the VIX Index
- Carr & Wu (2008): Variance Risk Premium


**历史**
COBE最初VIX的计算版本基于 Whaley(1993, 2000)，其针对S&P 100 index期权，使用ATM的期权的等权加权的BSM隐含波动率作为这个版本vix的估计。这种方法有2个主要缺陷，首先其依赖于BSM模型进行隐含波动率的计算，其次其忽略了其他期权所包含的信息。2003年后CBOE基于DDKZ的卖方研报切换了VIX的计算方法，并将标的改为S&P 500 index期权。

**假设**
市场价格连续不存在跳跃
$$
\frac{dS_t}{S_t} = \mu(t,...)dt + \sigma(t,...)dZ_t
$$

**variance forward**
假设市场上存在一个交割值为K的variance forward，则在无套利定价下其期货价格应当为
$$
\begin{aligned}
F &= E^Q[e^{-rT}(V - K)]
\end{aligned}
$$
其中V是实现variance。
$$
V = \frac{1}{T}\int_o^T\sigma^2(t,...)dt
$$
对于这样一个期货，其公平交割价格(使得F=0的K)是
$$
\begin{aligned}
K_{var} &= E^Q[V] \\
&=\frac{1}{T}E^Q[\int_o^T\sigma^2(t,...)dt]
\end{aligned}
$$
在有些文献中这种估计vix的方法又被称作variance swap rate的方法

**replicating variance forward**
由于瞬时方差未知，希望通过构建一个replicating portfolio的方式来估计$K_{var}$.
$$
\begin{aligned}
K_{var} &= \frac{1}{T}E^Q[\int_o^T\sigma^2(t,...)dt] \\
&= \frac{2}{T} E^Q[\int_0^T \frac{dS_t}{S_t} - d(logS_t)] \\ 
& =  \frac{2}{T} E^Q[\int_0^T\frac{dS_t}{S_t} - log(\frac{S_T}{S_0})]
\end{aligned}
$$
由上式的推到可以发现，对于方差的暴露可以通过2个position来获得:
    1. $\frac{1}{S_t}$股的动态underlying持仓
    2. log contract的静态持仓
    
其中1部分的期望由假设易得
$$
E^Q[\int_0^T \frac{dS_t}{S_t}] = rT
$$
2部分(静态log contract)则可以通过forward以及期权的组合来获得,详见appendix的intuition推导
$$
\begin{aligned}
\frac{S_T}{S_0} &= log\frac{S_T}{S_{\star}} + log\frac{S_{\star}}{S_0} \\ 
log\frac{S_T}{S_{\star}} & = \frac{S_T - S_{\star}}{S_{\star}} \\
&+\int_0^{S_\star} \frac{1}{k^2} Max(K-S_T, 0)dK \\
&+\int_{S_\star}^{\infty} \frac{1}{k^2} Max(S_T - K, 0)dK
\end{aligned}
$$
整合上述的结果即可得到vix的积分形式
$$
\begin{aligned}
K_{var} &= \frac{2}{T}[rT - (\frac{S_0}{S_{\star}}e^{rT} - 1) - log\frac{S_{\star}}{S_0} \\ 
& + e^{rT}\int_0^{S_{\star}} \frac{1}{K^2}P(K)dK \\
& + e^{rT}\int_{S_{\star}}^{\infty} \frac{1}{K^2}C(K)dK ]
\end{aligned}
$$
其中$S_{\star}$是一个可任意选定的数值，通常情况下，因为OTM的期权有更好的流动性，因此CBOE选择使用OTM的call与put进行计算，此时$S_{\star}$应当为spot price(或者其他用来判断是否OTM的价格)

**数值方法**
CBOE使用的numerical估计方法如下
$$
\begin{aligned}
\sigma^2 &= \frac{2}{T}\sum\frac{\Delta K_i}{K_i^2}e^{rT}Q(K_i) - \frac{1}{T}[\frac{F}{K_0} - 1]^2 \\
\Delta K_i &= \frac{K_{i+1} - K_{i-1}}{2}
\end{aligned}
$$

- 其中第一部分对应理论结果中期权积分的部分，本质上是一个矩形积分估计
- 其中第二部分为log contract部分泰勒展开后忽略二阶

**Demeterfi et al (1999) formula 形式**
$$
K_{var} = \frac{2 e^{rT}}{T}[e^{rT}\int_0^{F_0} \frac{1}{K^2}P(K)dK 
 + e^{rT}\int_{F_0}^{\infty} \frac{1}{K^2}C(K)dK ]]
$$
当选择DDKZ推导得到的vix中arbitrary的$S_{\star}$为$F_0$时(相同到期日的期权的价格)，$K_{var}$可以变形为上述形式。这种形式方便用于计算。Jiang & Tian(2007)的appendix中给出了完整的证明。 

**数值方法**
在Jiang & Tian (2005)与Jiang & Tian (2007)的文章中，详细讨论了使用cboe的计算方法带来的estimation error。他们通过simulation的方式发现2中最显著的误差分别是
1. discretion error: 来源于现实中期权strike并不是连续的。通常会导致高估vix的估计误差。
2. truncation error: 来源于现实中的期权strike并不是从0到无穷大的，会导致低估vix的估计误差。
在Carr & Wu(2008)的文章中也有相关的差值方法的描述。

1和2的问题可以通过对于implied volatility进行插值得到缓解。不对价格而是对于implied volatility进行插值的原因在于相比期权价格，implied volatility是更加平滑的。在这里依照Jiang & Tian和Carr & Wu的做法，通过内插使得任意两个strike之间的距离低于0.35 * atm implied vol。并且strike的upper bound与lower bound分别为 atm * exp(+- 8 * atm implied vol）。针对内部，通过cubic插值的方法(piecewise cubic hermite interpolating polynomial)的方法进行内部插值，从而解决discretion error 的问题。对于外部使用最大(小)strike对应的implied volatility进行平行外插从而解决truncation error的问题。外插不使用linear而是使用平行的原因在于linear外插有时会导致otm的implied volatility过高，从而导致了期权价格violation(otm price > atm price)

**BSM世界下使用$K^2$倒数加权期权组合**
$$
\begin{aligned}
vega &= \frac{\partial C}{\partial \sigma^2} = \frac{S\sqrt{\tau}}{2\sigma}\frac{exp(-d_1^2/2)}{\sqrt{2}\pi}\\
\Pi &= \int_{0}^{\infty} w(k) O(S, K, v) dK \\
vega_{\pi} &= \int_{0}^{\infty} w(k) vega_o(S,K,v) dK \\
\end{aligned}
$$
为了使得期权组合的vega不随underlying的价格变化而变化, 即使得其偏导为0
$$
\begin{aligned}
\frac{\partial vega_{\Pi}}{\partial S} &= 0 \\
\downarrow \\
2w(k) + K\frac{\partial w(k)}{\partial K} &= 0 \\
\downarrow \\ 
w(k) &= \frac{const}{K^2}
\end{aligned}
$$