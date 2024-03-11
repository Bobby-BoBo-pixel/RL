# @Time    : 2024/2/28 21:20
# @Author  : Bobby Johnson
# @Project : GuangZhou_FLC_Simplest.py
# @File    : PMV
# @Software: PyCharm
# @Targets : Calculate Predicted Mean Vote(PMV) 计算PMV

## ，，，。

#%%
import math
from math import exp
from math import pow
from math import sqrt

'''
    ta, 室内空气温度： air temperature (°C)
    tr, 室内平均辐射温度： mean radiant temperature (°C)
    vel, 室内风速： average air speed (Va) + activity-generated air speed (Vag) (m/s)
    rh, 相对湿度： relative humidity (%) Used only this way to input humidity level
    met, 人体代谢率： metabolic rate (met)
    clo, 服装热阻： clothing (clo)
    wme, 人体做功： external work, normally around 0 (met)
    returns: PMV和PPD组合成的tuple：(pmv, ppd)
    '''

def get_PMV(ta, rh):
    '''
    此程序根据室内温湿度用于计算PMV，是ANSI/ASHRAE 55-2023: Thermal Environmental Conditions for Human官方文档中的标准指定程序
    :param ta: 室内干球温度
    :param rh: 室内相对湿度
    :return: PMV：舒适度预测平均投票
    '''

    # 预设参数
    tr = ta         # 辐射温度设置为与室内温度相等
    vel = 0.1       # 风速设置为0.1 m/s
    met = 1.0       # 人体新陈代谢率设置为 1.0 (Met Unites)
    clo = 1.0       # 服装热阻设置为 1.0 clo
    wme = 0         # 人体对外无做功

    # 以下为正式计算
    pa = rh * 10 * exp(16.6536 - 4030.183 / (ta + 235))
    # 服装热阻： Thermal insulation of the clothing in M2K/W
    icl = 0.155 * clo
    # 新陈代谢率： Metabolic rate in W/M2
    m = met * 58.15
    # 人体做功： External work in W/M2
    w = wme * 58.15
    # 人体内部产热： Internal heat production in the human body
    mw = m - w
    # 根据服装热阻判断fcl的计算值
    if (icl <= 0.078):
        fcl = 1 + (1.29 * icl)
    else:
        fcl = 1.05 + (0.645 * icl)
    # 强迫对流传热系数： Heat transfer coefficient by forced convection
    hcf = 12.1 * sqrt(vel)
    # 室内空气绝对温度
    taa = ta + 273
    # 室内平均辐射绝对温度
    tra = tr + 273
    tcla = taa + (35.5 - ta) / (3.5 * icl + 0.1)
    p1 = icl * fcl
    p2 = p1 * 3.96
    p3 = p1 * 100
    p4 = p1 * taa
    p5 = 308.7 - 0.028 * mw + p2 * pow(tra / 100, 4)
    xn = tcla / 100
    xf = tcla / 50
    eps = 0.00015
    n = 0
    while abs(xn - xf) > eps:
        xf = (xf + xn) / 2
        hcn = 2.38 * pow(abs(100.0 * xf - taa), 0.25)
        if hcf > hcn:
            hc = hcf
        else:
            hc = hcn
        xn = (p5 + p4 * hc - p2 * pow(xf, 4)) / (100 + p3 * hc)
        n += 1
        if n > 150:
            print('Max iterations exceeded')
            return 1
    tcl = 100 * xn - 273
    # 皮肤散热： Heat loss diff. through skin
    hl1 = 3.05 * 0.001 * (5733 - (6.99 * mw) - pa)
    # 汗液蒸发散热： Heat loss by sweating
    if mw > 58.15:
        hl2 = 0.42 * (mw - 58.15)
    else:
        hl2 = 0
    # 呼吸潜热散热量： Latent respiration heat loss
    hl3 = 1.7 * 0.00001 * m * (5867 - pa)
    # 呼吸显热散热量： Dry respiration heat loss
    hl4 = 0.0014 * m * (34 - ta)
    # 辐射散热量： Heat loss by radiation
    hl5 = 3.96 * fcl * (pow(xn, 4) - pow(tra / 100, 4))
    # 对流散热量： Heat loss by convection
    hl6 = fcl * hc * (tcl - ta)
    ts = 0.303 * exp(-0.036 * m) + 0.028
    pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)
    ppd = 100.0 - 95.0 * math.exp(-0.03353 * pow(pmv, 4.0) - 0.2179 * pow(pmv, 2.0))
    return pmv      # 只返回PMV
    # return pmv, ppd

# 根据文档 ANSI/ASHRAE 55-2023: Thermal Environmental Conditions for Human 验证输出结果是否和验证表格一致
a = PMV(19.6, 19.6, 0.1, 86, 1.1, 1,0)
b = PMV(23.9,23.9,0.1,66,1.1,1,0)
# 按照表格，输出结果应该是：a = -0.47， b = 0.48
# if __name = '__main__'的意思是“如果当前模块是主程序执行的入口”: 只有在run此File的时候才会print，如果是其他File调用则不会print
if __name__ == '__main__':
    print(a)
    print(b)
