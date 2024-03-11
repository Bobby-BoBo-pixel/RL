# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 15:49:52 2023

@author: Administrator
"""
## 替换掉了i，只剩一个index作为索引变量
## 把室内设定温湿度去掉，需要在idf里面改，再导出
## 用了自己的实际模型，一小时12个步长（这里需要改）
## 去除掉了y1，也就是冷量的修正
## 也去除掉了室外风量对送风温度的影响

# 从EnergyPlus传出的变量主要有：T, RH_in
# 传入EnergyPlus的变量有：T_out, RH_out, Solar_out;  T_send, HR_send, Mass_send

# 程序目的：获取一天数据，从6月开始


from pyfmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt
from Control_FLC import cont        # 这里要换成强化学习控制
from conditioner import cond
from t_RH_ts import t_RH_ts
from Supply_calculation import supply
from Excel_Export import Excel_Export

# %%
'''
1 设置各种初始值
'''
# 设置初始值：各种运行时间
days = 1  # 模拟总时长
hours = 24
minutes = 60
seconds = 60
timestep = 12  # 步长长度
start_day = 31+28+31+30+31+30+31        # 8月1号，从1月总天数加到7月总天数，一共7个数
# step_num: 模拟总步长/个
step_num = days * hours * timestep
# sim_start: 模拟开始时间/s    (86400：一天有多少s)
sim_start = 86400 * start_day
# sim_time_all: 模拟总用时/s
sim_time_all = days * hours * minutes * seconds
# sim_stop: 模拟结束时间/s
sim_stop = sim_start + sim_time_all
# step_time: 步长间隔时间/s
step_time = (sim_stop - sim_start) / step_num
# step: 步长
step = np.linspace(1, step_num, step_num)
# %%
'''
2 加载模型并初始化
'''
# 加载FMU模型
fmu_name = 'GuangZhou_Heat_FMU_FLC_Simplest.fmu'        # 确定FMU文件名
model = load_fmu(fmu=fmu_name, log_level=7)             # 加载模型,创建一个model实例，并选择log_level为最高等级，7级，后续程序出问题可以查看生成的日志文件
# 加载options字典，并给ncp(number of communication points)赋值，否则默认值为500，可以查看下官方文档对option字典各键值对的解释
opts = model.simulate_options()         # 加载option字典，并赋值给opts
opts['ncp'] = step_num                  # 设置ncp为步长数，ncp其实就是模型需要模拟多少个步长
log = model.get_log()                   # 生成log日志文件(开始就报错的话，可以去看日志来解决问题)
print(log)                              # 打印日志
model.initialize(start_time=sim_start, stop_time=sim_stop)  # 确定模拟时间段，初始化


# %%
'''
3 创建各种空数列承接循环模拟数据
'''

# 从EnergyPlus中获取的重要参数数据
get_T = np.zeros((step_num, 1))         # EnergyPlus中室内温度
get_RH = np.zeros((step_num, 1))        # EnergyPlus中室内相对湿度
get_HR = np.zeros((step_num, 1))        # EnergyPlus中室内含湿量
get_T_out = np.zeros((step_num, 1))     # EnergyPlus中室外温度（用于计算送风温度）
get_HR_out = np.zeros((step_num, 1))    # EnergyPlus中室外含湿量（用于计算送风温度）
get_m_out = np.zeros((step_num, 1))     # EnergyPlus中室外新风量(用于计算送风温度)

# Python程序计算其他参数所用的参数
Tw = np.zeros((step_num, 1))            # 中间变量，用于计算冷量，EnergyPlus中获取不了
delta_T = np.zeros((step_num, 1))       # 温度误差
delta_T_c = np.zeros((step_num, 1))     # 温度变化率
delta_RH = np.zeros((step_num, 1))      # 湿度误差
delta_RH_c = np.zeros((step_num, 1))    # 湿度变化率
speed = np.zeros((step_num, 2))         # 压缩机风机转速
cooling_load = np.zeros((step_num, 2))  # 显热+潜热冷量

# 向EnergyPlus传输的数据
# 根据神经网络输出的冷量计算的送风参数及空调开关
to_T_supply = np.zeros((step_num, 1))   # 送风温度
to_HR_supply = np.zeros((step_num, 1))  # 送风含湿量
to_m_supply = np.zeros((step_num, 1))   # 送风质量流量
Switch = np.zeros((step_num, 1))        # 空调开关

## 获取的验证数据
get_Qs_zone = np.zeros((step_num, 1))
get_Ql_zone = np.zeros((step_num, 1))
get_Qt_zone = np.zeros((step_num, 1))
get_Qs_supplyair = np.zeros((step_num, 1))
get_Ql_supplyair = np.zeros((step_num, 1))
get_Qt_supplyair = np.zeros((step_num, 1))


# %%
'''
4 设置空调送风参数和空调开关，模拟一个步长
'''
# 设置索引变量
i = 0
get_T[i] = model.get('T')  # 设置室内初始温度为EnergyPlus里面设置的Tin
get_RH[i] = model.get('RH')  # 设置室内初始湿度为EnergyPlus里面设置的RH
T_ini = 27
RH_ini = 50
C_ini = 55                                                      # 初始压缩机频率55
F_ini = 625
while sim_start < sim_stop:
    if i == 0:
        # 向EnergyPlus传输初始送风温湿度、质量流量
        model.set('ep_T_supply', 18.55)         # 设置初始送风温度
        model.set('ep_HR_supply', 0.008)        # 设置初始送风湿度
        model.set('ep_m_supply', 0.3)           # 设置初始送风量
        # 计算空调开关值：根据获取的室内温湿度初始值
        if (T_ini < 23):  # 开启空调阈值23℃
            Ava = 0
        if (T_ini >= 23):
            Ava = 1
    else:
        model.set('ep_HR_supply', to_HR_supply[i - 1])
        model.set('ep_m_supply', to_m_supply[i - 1])
        model.set('ep_T_supply', to_T_supply[i - 1])
        if (get_T[i-1] < 23):  # 开启空调阈值23℃
            Ava = 0
        if (get_T[i-1] >= 23):
            Ava = 1
    Switch[i] = Ava                     # Switch为开关情况数组，Ava为此时间步长的空调开关情况
    # 向EnergyPlus传输开关值
    model.set('ep_switch', Ava)             # 设置EnergyPlus里空调开关的开闭为Ava
    # 运行一个时间步长
    model.do_step(current_t=sim_start, step_size=step_time, new_step='True')

    # %%
    '''
    5 运行一个时间步长后从模型中获取数据
    '''
    # 从模型中获取数据
    # 获取室内温湿度
    get_T[i] = model.get('T')               # 获取室内温度
    get_RH[i] = model.get('RH')             # 获取室内相对湿度
    get_HR[i] = model.get('HR')             # 获取室内含湿量 Humidity Ratio(用于计算送风含湿量)
    # 获取室外温度（压缩机功率需要用到）
    get_T_out[i] = model.get('T_out')       # 获取室外温度

    # 获取验证数据
    get_Qs_zone[i] = model.get('Qs_1')
    get_Ql_zone[i] = model.get('Ql_1')
    get_Qt_zone[i] = model.get('Qt_1')
    get_Qs_supplyair[i] = model.get('Qs')
    get_Ql_supplyair[i] = model.get('Ql')
    get_Qt_supplyair[i] = model.get('Qt')
    # %%
    '''
    6 利用运行一个时间步长的参数来计算下一时刻送风参数 （这里用到控制算法）
    '''
    # 计算控制算法和空调模型所需参数
    Tw[i] = t_RH_ts(get_T[i], get_RH[i] / 100)          # 计算湿球温度
    delta_T[i] = get_T[i] - 25  # 与目标温度误差，设置的目标为25℃
    delta_RH[i] = get_RH[i] - 50  # 与目标湿度误差，设置的目标为50%
    if i ==0:
        delta_T_c[i] = get_T[i] - T_ini  # 与初始温度误差
        delta_RH_c[i] = get_RH[i] - RH_ini  # 与初始湿度误差
        speed[i] = cont(float(T_ini), float(get_T[i, 0]), float(RH_ini), float(get_RH[i, 0]), C_ini, F_ini)
    else:
        delta_T_c[i] = get_T[i] - T_ini  # 与初始温度误差
        delta_RH_c[i] = get_RH[i] - RH_ini  # 与初始湿度误差
        speed[i] = cont(float(get_T[i - 1, 0]), float(get_T[i, 0]), float(get_RH[i - 1, 0]), float(get_RH[i, 0]),
                        float(speed[i - 1, 0]), float(speed[i - 1, 1]))  # 根据算法获取压缩机风机转速

    y1 = 0.766956 + 0.0107756 * Tw[i] - 0.0000414703 * Tw[i] ** 2 + 0.00134961 * get_T_out[i] - 0.000261144 * get_T_out[
        i] ** 2 + 0.000457488 * Tw[i] * get_T_out[i]
    cooling_load[i] = cond(get_T[i, 0], Tw[i, 0], speed[i, 0],
                               speed[i, 1] / 1250 * 100)*y1  # [i,0]是因为要维度相同
    # 调用函数计算出送风数据
    supply_params = supply(get_T[i], get_HR[i], cooling_load[i])
    to_T_supply[i] = supply_params[0]
    to_HR_supply[i] = supply_params[1]
    to_m_supply[i] = supply_params[2]                       # 风量固定0.3kg/s
    # 所有送风参数计算完后再加时间步长
    i += 1
    sim_start += step_time                                  # sim_start这个参数必须要变化，因为do_step进行模拟需要这个参数每次变化一个step_time

# # %%
# '''
# 7 计算后续时刻
# '''
# # 计算T0之后
#
# while sim_start < sim_stop:
#     # 上一时刻计算的送风参数输入
#     model.set('ep_HR_supply', to_HR_supply[i-1])
#     model.set('ep_m_supply', to_m_supply[i-1])
#     model.set('ep_T_supply', to_T_supply[i-1])
#     # 根据上一时刻室内温度判断是否开空调
#     if (get_T[i-1] < 23):
#         Ava = 0
#     if (get_T[i-1] >= 23):
#         Ava = 1
#     # 向EnergyPlus中传输空调开关信号
#     Switch[i] = Ava
#     model.set('ep_switch', Ava)
#     # 继续进行模拟
#     model.do_step(current_t=sim_start, step_size=step_time, new_step='True')
#
#     # 从EnergyPlus获取数据
#     get_T[i] = model.get('T')       # 获取室内温度
#     get_RH[i] = model.get('RH')     # 获取室内湿度
#     get_HR[i] = model.get('HR')     # 获取室内含湿量
#     get_T_out[i] = model.get('T_out')       # 获取室外温度
#     get_HR_out[i] = model.get('HR_out')     # 获取室外湿度
#     get_m_out[i] = model.get('m_out')       # 获取室外风量
#
#     # 获取验证数据
#     get_Qs_zone[i] = model.get('Qs_1')
#     get_Ql_zone[i] = model.get('Ql_1')
#     get_Qt_zone[i] = model.get('Qt_1')
#     get_Qs_supplyair[i] = model.get('Qs')
#     get_Ql_supplyair[i] = model.get('Ql')
#     get_Qt_supplyair[i] = model.get('Qt')
#
#     # 根据获取数据进行计算
#     delta_T[i] = get_T[i] - 25  # 计算温度误差
#     delta_T_c[i] = get_T[i] - get_T[i-1]  # 计算温度变化率
#     delta_RH[i] = get_RH[i] - 50  # 计算湿度误差
#     delta_RH_c[i] = get_RH[i] - get_RH[i-1]  # 计算湿度变化率
#     speed[i] = cont(float(get_T[i-1, 0]), float(get_T[i, 0]), float(get_RH[i-1, 0]), float(get_RH[i, 0]),
#                     float(speed[i-1, 0]), float(speed[i-1, 1]))  # 根据算法获取压缩机风机转速
#     Tw[i] = t_RH_ts(get_T[i], get_RH[i] / 100)  # 计算湿球温度
#     y1 = 0.766956 + 0.0107756 * Tw[i] - 0.0000414703 * Tw[i] ** 2 + 0.00134961 * get_T_out[i] - 0.000261144 * get_T_out[
#         i] ** 2 + 0.000457488 * Tw[i] * get_T_out[i]
#     cooling_load[i] = cond(float(get_T[i]), float(Tw[i]), speed[i, 0], speed[i, 1] / 1250 * 100)  # 计算冷量
#
#     # 调用函数计算出送风数据
#     supply_params = supply(get_T[i], get_HR[i], cooling_load[i])
#     to_T_supply[i] = supply_params[0]
#     to_HR_supply[i] = supply_params[1]
#     to_m_supply[i] = supply_params[2]  # 风量固定0.3kg/s
#
#     # 索引参数及sim_star变化
#     i += 1
#     sim_start += step_time # 模拟时间增加timestep(因为do_step需要sim_start变化)



#%%
'''
7 画图
'''
plt.plot(step, get_T, label='T')
plt.plot(step, get_RH, label='RH')
plt.show()

# #%%
# '''
# 8 把验证数据等导入到excel表
# '''
# # 创建需要导出到Excel的参数字典
# dic = {'cooling_sensible': cooling_load[:,0],'get_Qs_zone': get_Qs_zone[:,0], 'get_Qs_supplyair': get_Qs_supplyair[:,0], } # [:,0]的意思是取第一列的所有行，把二维ndarray变成一维array，字典不能把键值对中的值value设成二维
# # 调用Excel_Export.py文件中的To_Excel函数，把数据导出到a.xlsx的excel文件中
# file_name = 'a.xlsx'                                          # file_name只有文件名就是在project里面生成excel
# # file_name = r"C:\Users\Bobby\Desktop\a.xlsx"                # 也可以放置到桌面上，必须要加r，选用a的原因是a.xlsx可以在project的最上面
# Excel_Export(dic,file_name)
