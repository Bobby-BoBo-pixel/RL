# @Time    : 2024/3/5 15:35
# @Author  : Bobby Johnson
# @Project : GuangZhou_FLC_Simplest.py
# @File    : Supply_calculation
# @Software: PyCharm
# @Targets :
'''
湿空气焓值：  h=1.005t + d（2500+1.84t)        kJ/kg干空气
湿空气显热：  sensible = 1.005+1.84td         kJ/kg干空气
湿空气潜热：  latent = 2500d                  kJ/kg干空气
显热冷量：   cooling_sensible = 回风显热 - 送风显热
潜热冷量：   cooling_latent = 回风潜热 - 送风潜热
d：含湿量
t：温度
h：焓值
'''


def supply(get_T, get_HR, cooling):
    '''
    根据Energyplus获取的室内回风温湿度和空调模型计算出的冷量获取送风参数
    :param get_T: EnergyPlus中获取的回风温度        ℃
    :param get_HR: EnergyPlus中获取的回风含湿量      kg/kg干空气
    :param cooling: 空调模型计算出的冷量              W
    :return: T_supply,HR_supply,m_supply： 送风温湿度+送风量
    '''
    # 把冷量解包，换算成kW
    cooling_sensible = cooling[0]/1000      # kW
    cooling_latent = cooling[1]/1000        # kW
    # 固定送风量
    m_supply = 0.3                          # 0.3kg/s
    # 计算送风前后含湿量差
    delta_d = cooling_latent/2500/0.3       # kg/kg干空气
    # 计算送风含湿量
    HR_supply = get_HR - delta_d            # kg/kg干空气
    # 计算回风显热
    sensible_return = (1.01+1.84*get_HR)*get_T                      # kW
    # 计算送风显热
    sensible_supply = sensible_return - cooling_sensible/0.3            # kW
    # 计算送风温度
    T_supply = sensible_supply/(1.01+1.84*HR_supply)                # ℃
    return T_supply,HR_supply,m_supply
