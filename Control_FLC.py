# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 15:49:52 2023

@author: Administrator
"""
# 从EnergyPlus传出的变量主要有：T, RH_in
# 传入EnergyPlus的变量有：T_out, RH_out, Solar_out;  T_send, HR_send, Mass_send

# 程序目的：获取一天数据，从6月开始


import pyfmi
from pyfmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt
import csv
from control import cont
from conditioner import cond
from t_RH_ts import t_RH_ts
import xlrd

# %%
'''
1 设置各种初始值
'''
# 设置初始值：各种运行时间
days = 1  # 模拟总时长
hours = 24
minutes = 60
seconds = 60
timestep = 60  # 步长长度
start_day = 201
# step_num: 模拟总步长/个
step_num = days * hours * timestep
# sim_start: 模拟开始时间/s    (86400：一天有多少s，151是指从6月份开始进行模拟，1月1日到6月1日大概151天)
sim_start = 86400 * start_day
# sim_time: 模拟总用时/s
sim_time = days * hours * minutes * seconds
# sim_stop: 模拟结束时间/s
sim_stop = sim_start + sim_time
# step_time: 步长间隔时间/s
step_time = (sim_stop - sim_start) / step_num

# %%
'''
2 加载模型
'''
# 加载模型,创建一个model实例
fmu_name = 'GuangZhou_Heat_FMU_1.fmu'
model = load_fmu(fmu=fmu_name, log_level=7)
# 加载options字典，并把ncp(number of communication points)和initialize赋值
opts = model.simulate_options()  # 模拟选项全部选用默认值（视频）
opts['ncp'] = step_num  # 设置ncp为步长数
opts['initialize'] = True  # 确定初始化(这一行其实不用，因为default就是True)
log = model.get_log()  # 生成log日志文件
print(log)
model.initialize(start_time = sim_start, stop_time = sim_stop)  # 确定模拟时间段，初始化
t = np.linspace(sim_start + step_time, sim_stop, step_num)  # 时间轴（即每个步长所在的时间点，这里加入step_time也是因为linspace前后都包括）

# %%
'''
3 创建各种空数列承接循环模拟数据
'''
index = 0

# 从EnergyPlus中获取的参数数据
get_T = np.zeros((step_num, 1))  # EnergyPlus中室内温度
get_RH = np.zeros((step_num, 1))  # EnergyPlus中室内相对湿度
get_HR = np.zeros((step_num, 1))  # EnergyPlus中室内含湿量
# 下面这部分EnergyPlus获取的数据不是核心，仅起到验证是否正常运行的作用
get_Tw = np.zeros((step_num, 1))  # EnergyPlus中室内湿球温度
get_T_out = np.zeros((step_num, 1))  # EnergyPlus中室外温度（用于验证）
get_HR_out = np.zeros((step_num, 1))  # EnergyPlus中室外含湿量（用于验证）
get_m_out = np.zeros((step_num, 1))  # EnergyPlus中室外风量(不知道用来干什么的)
get_Tem_set = np.zeros((step_num, 1))  # EnergyPlus中送风温度（用于验证）
get_HR_set = np.zeros((step_num, 1))  # EnergyPlus中送风含湿量（用于验证）
get_Mass_set = np.zeros((step_num, 1))  # EnergyPlus中送风质量流量（用于验证）
get_latent1 = np.zeros((step_num, 1))  # EnergyPlus中潜热（用于验证）
get_Solar_diffuse = np.zeros((step_num, 1))  # EnergyPlus中光照散射强度（用于验证）
get_Solar_direct = np.zeros((step_num, 1))  # EnergyPlus中光照直射强度（用于验证）
get_Qs = np.zeros((step_num, 1))  # EnergyPlus中显热冷量（用于验证）
get_Ql = np.zeros((step_num, 1))  # EnergyPlus中潜热冷量（用于验证）
get_Qt = np.zeros((step_num, 1))  # EnergyPlus中总冷量（用于验证）

# Python程序中计算参数
# 权重模糊逻辑控制算法需要的数据
delta_T = np.zeros((step_num, 1))  # 温度误差
delta_T_c = np.zeros((step_num, 1))  # 温度变化率
delta_RH = np.zeros((step_num, 1))  # 湿度误差
delta_RH_c = np.zeros((step_num, 1))  # 湿度变化率
Pc = np.zeros((step_num, 1))  # 压缩机功率（强化学习控制算法需要的数据）
Pf = np.zeros((step_num, 1))  # 风机功率（强化学习控制算法需要的数据）
P = np.zeros((step_num, 1))  # 总功率（强化学习控制算法需要的数据）
# 控制算法输出数据
speed = np.zeros((step_num, 2))  # 压缩机风机转速
# 神经网络根据算法输出计算出的冷量数据
cooling_load = np.zeros((step_num, 2))  # 显热+潜热冷量
# 根据神经网络输出的冷量计算的送风参数
to_m_supply = np.zeros((step_num, 1))  # 送风质量流量
to_T_supply = np.zeros((step_num, 1))  # 送风温度
to_HR_supply = np.zeros((step_num, 1))  # 送风含湿量
# 其他参数
Switch = np.zeros((step_num, 1))  # 空调开关
# Ave_sensible = np.zeros((step_num, 1))  # 平均显热
# Ave_latent = np.zeros((step_num, 1))  # 平均潜热
# Ave_Pc = np.zeros((step_num, 1))  # 平均压缩机功率
# Ave_Pf = np.zeros((step_num, 1))  # 平均风机功率

# %%
'''
4 初始化 计算T0时刻
'''

# 设置初始室内条件
T_ini = model.get('T')  # 设置室内初始温度为EnergyPlus里面设置的Tin，是多少？
RH_ini = model.get('RH')  # 设置室内初始湿度为EnergyPlus里面设置的RH，是多少？

# 设置初始室外条件，这里使用天气文件作为室外条件
model.set('ep_T_out', 31)  # 设置室外初始温度
model.set('ep_RH_out', 60)  # 设置室外初始湿度

# 设置初始送风温湿度、质量流量
model.set('ep_T_supply', 18.55)  # 设置初始送风温度
model.set('ep_HR_supply', 0.008)  # 设置初始送风湿度
model.set('ep_m_supply', 0.3)  # 设置初始送风量
# 准备好初始化所需的数据后，设置空调开启条件，阈值温度为23℃
if (T_ini < 23):  # 开启空调条件
    Ava = 0
if (T_ini >= 23):
    Ava = 1

# 设置空调开关数组
Switch[index] = Ava  # Switch为开关情况数组，Ava为此时间步长的空调开关情况
model.set('ep_switch', Ava)  # 设置energyplus里空调开关的开闭为Ava
# 运行一个时间步长
res = model.do_step(current_t=sim_start, step_size=step_time, new_step='True')  # 如何控制停止呢

# %%
'''
5 运行一个时间步长后从模型中获取数据
'''
i = index + 1
# 从模型中获取数据
# 获取室内温湿度
get_T[i] = model.get('T')  # 获取室内温度
get_RH[i] = model.get('RH')  # 获取室内相对湿度
get_HR[i] = model.get('HR')  # 含湿量 Humidity Ratio
# 获取冷量（为了后面对2h进行平均）
get_Qs[i] = model.get('Qs')  # 获取显热冷量
get_Qt[i] = model.get('Qt')  # 获取全热冷量
get_Ql[i] = model.get('Ql')  # 获取显热冷量
get_Solar_diffuse[i] = model.get('Solar_diffuse')
get_Solar_direct[i] = model.get('Solar_direct')
# 获取室外温度（压缩机功率需要用到）
get_T_out[i] = model.get('T_out')  # 获取室外温度
to_T_supply[i] = model.get('T_supply')  # 获取系统节点温度 system node temperature（各个部件的节点温度）

# %%
'''
6 利用运行一个时间步长的参数来计算下一时刻送风参数 
'''
# 计算温湿度误差和变化率
delta_T[index] = get_T[i] - 25  # 与目标温度误差，设置的目标为25℃
delta_T_c[index] = get_T[i] - T_ini  # 与初始温度误差
delta_RH[index] = get_RH[i] - 50  # 与目标湿度误差，设置的目标为50%
delta_RH_c[index] = get_RH[i] - RH_ini  # 与初始湿度误差
C_ini = 55  # 初始压缩机频率55
F_ini = 625  # 初始风机转速625
# 调用控制算法及空调模型
speed[index] = cont(float(T_ini), float(get_T[index]), float(RH_ini), float(get_RH[index]), C_ini,
                    F_ini)  # 控制算法输出下一时刻的压缩机风机转速(输出一个tuple，tuple中第一个是压缩机，第二个是风机)
get_Tw[index] = t_RH_ts(get_T[index], get_RH[index] / 100)  # 计算湿球温度, 注意这个get_Tw不是直接从EP中获取的，而是通过获取数据计算的
cooling_load[index] = cond(get_T[index, 0], get_Tw[index, 0], speed[index, 0],
                           speed[index, 1] / 1250 * 100)  # 引用空调模型（输出一个tuple（CCs，CCl））
# 计算出送风数据
to_m_supply[index] = 0.3  # 风量固定0.3kg/s
delta_d = cooling_load[
             index, 1] / 2500 / 0.3 / 1000  # 蒸发器进出口含湿量偏差（计算潜热冷量需要的）  h=1.005t + d（2500+1.84t) 2500是汽化潜热，0.3是风量，1000是单位换算/
to_HR_supply[index] = get_HR[index] - delta_d  # 送风含湿量 = 回风含湿量 - 含湿量差
to_T_supply[index] = (1840 * get_HR[index] * get_T[index] + 1010 * get_T[index] - cooling_load[index, 0] / 0.3) / (
        1010 + 1840 * to_HR_supply[index])  # 送风温度
# 加时间步长
sim_start += step_time

# %%
'''
7 计算后续时刻
'''
# 计算T0之后
for daynum in range(1, 2):
    countdown = sim_stop - step_time  # 每运行一次减去一个步长时间，在倒计时
    while sim_start < countdown:

        # 往EnergyPlus传输值
        # 室外参数4个
        model.set('ep_T_out', 30)  # 设置室外条件，这里使用天气文件作为室外条件
        model.set('ep_RH_out', 70)
        model.set('ep_Solar_diffuse', 300)
        model.set('ep_Solar_direct', 500)
        # 送风参数3个
        model.set('ep_HR_supply', to_HR_supply[index])
        model.set('ep_m_supply', to_m_supply[index])
        model.set('ep_T_supply', to_T_supply[index])
        # 从EnergyPlus里获取温湿度（一开始是初始温湿度）
        get_T[index] = model.get('T')
        get_RH[index] = model.get('RH')
        # 根据室内温度判断是否开空调
        if (get_T[index] < 23):
            Ava = 0
        if (get_T[index] >= 23):
            Ava = 1
            # 计算功率
            Pc[index] = 2823 - 115.1 * get_T_out[index] - 43.2 * speed[index, 0] + 2.722 * speed[index, 0] * get_T_out[
                index]  # 计算压缩机功率
            Pf[index] = 0.2011 * speed[index, 1] / 1250 * 100 ** 2 - 7.855 * speed[
                index, 1] / 1250 * 100 + 244.47  # 计算风机功率
            P[index] = Pc[index] + Pf[index]  # 计算总功率
        # 向EnergyPlus中传输空调开关信号

        model.set('ep_switch', Ava)
        model.set('ep_T_set', 27)
        model.set('ep_RH_set', 47)
        model.set('ep_m_out', 0)  # 设置外界为无风状态
        # 继续进行模拟
        res = model.do_step(current_t=sim_start, step_size=step_time, new_step='True')
        i = index + 1
        Switch[i] = Ava
        # 继续从EnergyPlus获取数据
        get_T[i] = model.get('T')  # 获取室内温度
        get_RH[i] = model.get('RH')  # 获取室内湿度
        get_HR[i] = model.get('HR')  # 获取室内含湿量
        get_Qs[index] = model.get('Qs')  # 获取显热
        get_Ql[index] = model.get('Ql')
        get_latent1[index] = model.get('Ql_1')  # 获取潜热(为什么不用Ql)
        get_Qt[index] = model.get('Qt')  # 获取全热
        get_T_out[i] = model.get('T_out')  # 获取室外温度
        get_HR_out[i] = model.get('HR_out')  # 获取室外湿度  OA：outdoor air
        get_m_out[i] = model.get('m_out')  # 获取室外风量 kg/s (这个是干嘛的)
        get_Tem_set[i] = model.get('T_supply')  # 获取送风温度
        get_Mass_set[i] = model.get('m_supply')  # 获取送风量 kg/s
        get_HR_set[i] = model.get('HR_supply')  # 获取送风含湿量
        get_Solar_diffuse[i] = model.get('Solar_diffuse')
        get_Solar_direct[i] = model.get('Solar_direct')

        # 根据获取数据进行计算
        delta_T[i] = get_T[i] - 25  # 计算温度误差
        delta_T_c[i] = get_T[i] - get_T[index]  # 计算温度变化率
        delta_RH[i] = get_RH[i] - 50  # 计算湿度误差
        delta_RH_c[i] = get_RH[i] - get_RH[index]  # 计算湿度变化率
        speed[i] = cont(float(get_T[index, 0]), float(get_T[i, 0]), float(get_RH[index, 0]), float(get_RH[i, 0]),
                        float(speed[index, 0]), float(speed[index, 1]))  # 根据算法获取压缩机风机转速
        get_Tw[i] = t_RH_ts(get_T[i], get_RH[i] / 100)  # 计算湿球温度
        y1 = 0.766956 + 0.0107756 * get_Tw[i] - 0.0000414703 * get_Tw[i] ** 2 + 0.00134961 * get_T_out[
            i] - 0.000261144 * get_T_out[
                 i] ** 2 + 0.000457488 * get_Tw[i] * get_T_out[i]  # y1是计算冷量必须的
        cooling_load[i] = cond(float(get_T[i]), float(get_Tw[i]), speed[i, 0], speed[i, 1] / 1250 * 100) * y1  # 计算冷量

        # 计算出来的送风参数送入EnergyPlus
        to_m_supply[i] = 0.3  # 风量0.3kg/s固定
        delta_d = float(cooling_load[i, 1]) / 2500 / 0.3 / 1000  # 蒸发器前后含湿量差,2500是水的蒸发潜热，0.3是流量kg
        to_HR_supply[i] = get_HR[i] - delta_d  # 送风（蒸发器进口）含湿量
        to_T_supply[i] = (1010 * get_T_out[i] * get_m_out[i] + 1840 * get_HR_out[i] * get_T_out[i] * get_m_out[
            i] + 1010 * get_T[i] * (
                                  to_m_supply[i] - get_m_out[i]) + 1840 * get_HR[i] * get_T[i] * (
                                      to_m_supply[i] - get_m_out[i]) - cooling_load[i, 0]) / (
                                 1010 * get_m_out[i] + 1840 * get_HR_out[i] * get_m_out[i] + 1010 * (
                                 to_m_supply[i] - get_m_out[i]) + 1840 * get_HR[i] * (
                                             to_m_supply[i] - get_m_out[i]))  # 计算送风温度
        index += 1
        sim_start += step_time  # 模拟时间增加timestep(正好对应do_step的参数)
    # sum_sensible = 0
    # sum_latent = 0
    # sum_Pc = 0
    # sum_Pf = 0
    # # 提取数据，只获取12-14点两个小时进行平均
    # for minute in range(719 + (daynum - 1) * 1440, 839 + (daynum - 1) * 1440):
    #     sum_sensible += get_Qs[minute]
    #     sum_latent += get_latent1[minute]
    #     sum_Pc += Pc[minute]
    #     sum_Pf += Pf[minute]
    # Ave_sensible[daynum - 1] = sum_sensible / 120  # 计算两小时内平均显热
    # Ave_latent[daynum - 1] = sum_latent / 120  # 计算两小时内平均潜热
    # Ave_Pc[daynum - 1] = sum_Pc / 120  # 计算两小时内平均压缩机功率
    # Ave_Pf[daynum - 1] = sum_Pf / 120  # 计算两小时内平均风机功率

# 算30天，30组室外温湿度条件，每组控空调在12点-下午2点的平均前棱和嫌冷
# %%
'''
7 画图 
'''
# plt.subplot(1,2,2)
plt.plot(t, get_T, label='T')
plt.plot(t,get_RH, label = 'RH')
plt.show()
plt.plot(t,get)

# plt.subplot(1,2,1)
# plt.plot(t,RH)
