# @Time    : 2024/2/28 16:59
# @Author  : Bobby Johnson
# @Project : GuangZhou_FLC_Simplest.py
# @File    : Control_RL
# @Software: PyCharm
# @Targets :

# 导入actor和critic实例
from Networks import actor, critic
from Get_Data import get_data
from Weather import get_weather
from PMV import get_PMV
from Electricity_Price import get_electricity_price
#%%
'''
1 定义神经网络
'''


#%%
'''
2 获取数据
'''
# get_data调用control_RL函数，获取动作
def control_RL(T_out, HR_out, Solar_direct, T_out_ini, T,HR,PMV,T_c,HR_c,PMV_c,Cs,Fs,Price_t,Price_t1, t, t1):
    return 0
# 调用get_data获取30天数据
indoor_params = get_data()
#%%
'''
3 训练神经网络
'''
# get_data获取室内数据（室内温湿度及其变化率）
indoor_params = get_data()
# get_PMV获取PMV数值（）
PMV = get_PMV()
# weather获取室外数据（室外温湿度及辐射）
outdoor_params = get_weather()
# speed函数获取压缩机风机转速
# get_electricity_price函数获取电价信息






