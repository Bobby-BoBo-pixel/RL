# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 15:49:52 2023

@author: Administrator
"""
## 把PMV计算直接加进来了
## 把index换成了i
## delta_Variable系列换成了Variable_c
## 加上了神经网络需要的所有参数（都改到了神经网络所需数据里面），并调用神经网络前向传播获取speed
## 其中室外天气变化只选用了ep中进行线性插值的（为了先跑出数据）
## 剔除掉了冗余代码
## get_variable系列统一改成ep_variable

# 从EnergyPlus传出的变量主要有：T, RH_in
# 传入EnergyPlus的变量有：T_out, RH_out, Solar_out;  T_send, HR_send, Mass_send



from pyfmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt
from Control_RL import control_RL
from conditioner import cond
from t_RH_ts import t_RH_ts
from t_HR_ts import t_HR_ts
from Supply_calculation import supply
from Excel_Export import Excel_Export
from PMV import get_PMV
from Electricity_Price import get_electricity_price
def get_data():

    # %%
    '''
    1 设置各种初始值
    '''
    # 设置初始值：各种运行时间
    days = 30  # 模拟总时长
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

    # 神经网络需要获取的数据（共16个，speed中包含两个）
    ep_T = np.zeros((step_num, 1))          # 室内温度--EnergyPlus中
    ep_HR = np.zeros((step_num, 1))         # 室内含湿量--EnergyPlus中
    PMV = np.zeros((step_num, 1))           # 室内PMV
    T_c = np.zeros((step_num, 1))           # 室内温度变化率
    HR_c = np.zeros((step_num, 1))          # 室内含湿量变化率
    PMV_c = np.zeros((step_num, 1))         # 室内PMV变化率
    ep_T_out = np.zeros((step_num, 1))              # 室外温度（EnergyPlus中，用于计算送风温度）
    ep_HR_out = np.zeros((step_num, 1))             # 室外含湿量（EnergyPlus中，用于计算送风温度）
    ep_Solar_direct = np.zeros((step_num, 1))       # 室外含湿量（EnergyPlus中，用于计算送风温度）
    T_out_ini = 30                                  # 室外初始温度
    Elec_price = np.zeros((step_num, 1))                    # 目前电价
    Elec_price1 = np.zeros((step_num, 1))                   # 下一时刻电价
    t = np.zeros((step_num, 1))                                         # 目前时刻
    t1 = np.zeros((step_num, 1))                                        # 下次电价改变时刻
    speed = np.zeros((step_num, 2))         # 压缩机风机转速

    # Python程序计算其他参数所用的参数
    ep_RH = np.zeros((step_num, 1))         # 室内相对湿度--EnergyPlus中
    RH_c = np.zeros((step_num, 1))          # 室内相对湿度变化率
    Tw = np.zeros((step_num, 1))            # 中间变量，用于计算冷量，EnergyPlus中获取不了
    cooling_load = np.zeros((step_num, 2))  # 显热+潜热冷量

    # 向EnergyPlus传输的数据
    to_T_supply = np.zeros((step_num, 1))   # 送风温度
    to_HR_supply = np.zeros((step_num, 1))  # 送风含湿量
    to_m_supply = np.zeros((step_num, 1))   # 送风质量流量
    Switch = np.zeros((step_num, 1))        # 空调开关

    ## 需从EnergyPlus获取的验证数据
    ep_Qs_zone = np.zeros((step_num, 1))
    ep_Ql_zone = np.zeros((step_num, 1))
    ep_Qt_zone = np.zeros((step_num, 1))
    ep_Qs_supplyair = np.zeros((step_num, 1))
    ep_Ql_supplyair = np.zeros((step_num, 1))
    ep_Qt_supplyair = np.zeros((step_num, 1))
    ep_m_out = np.zeros((step_num, 1))      # 新风量--室外送入新风(EnergyPlus中，用于计算送风温度)

    # %%
    '''
    4 设置空调送风参数和空调开关
    '''
    # 设置索引变量
    i = 0
    ep_T[i] = model.get('T')  # 设置室内初始温度为EnergyPlus里面设置的Tin
    ep_HR[i] = model.get('HR')  # 设置室内初始湿度为EnergyPlus里面设置的RH
    ep_RH[i] = model.get('HR')
    T_ini = 25
    RH_ini = 50
    HR_ini = 0.00988
    C_ini = 55
    F_ini = 625
    while sim_start < sim_stop:
        if i == 0 :
            # 向EnergyPlus传输初始送风温湿度、质量流量
            model.set('ep_T_supply', 18.55)         # 设置初始送风温度
            model.set('ep_HR_supply', 0.008)        # 设置初始送风湿度
            model.set('ep_m_supply', 0.3)           # 设置初始送风量
            # 计算空调开关值：根据获取的室内温湿度初始值
                            # 设置室内初始含湿量为EnergyPlus里面设置的HR
            if (T_ini < 23):                        # 开启空调阈值23℃
                Ava = 0
            if (T_ini >= 23):
                Ava = 1
        else:
            model.set('ep_HR_supply', to_HR_supply[i - 1])
            model.set('ep_m_supply', to_m_supply[i - 1])
            model.set('ep_T_supply', to_T_supply[i - 1])
            if (ep_T[i - 1] < 23):  # 开启空调阈值23℃
                Ava = 0
            if (ep_T[i - 1] >= 23):
                Ava = 1
        Switch[i] = Ava                         # Switch为开关情况数组，Ava为此时间步长的空调开关情况
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
        ep_T[i] = model.get('T')                # 获取室内温度
        ep_RH[i] = model.get('RH')              # 获取室内含湿量 Humidity Ratio(用于计算送风含湿量)
        ep_HR[i] = model.get('HR')              # 获取室内含湿量 Humidity Ratio(用于计算送风含湿量)
        # 获取室外温度（压缩机功率需要用到）
        ep_T_out[i] = model.get('T_out')        # 获取室外温度
        ep_HR_out[i] = model.get('HR_out')      # 获取室外含湿量
        ep_Solar_direct[i] = model.get('Solar_direct')      # 获取室外太阳直射

        # 获取验证数据
        ep_Qs_zone[i] = model.get('Qs_1')
        ep_Ql_zone[i] = model.get('Ql_1')
        ep_Qt_zone[i] = model.get('Qt_1')
        ep_Qs_supplyair[i] = model.get('Qs')
        ep_Ql_supplyair[i] = model.get('Ql')
        ep_Qt_supplyair[i] = model.get('Qt')
        # %%
        '''
        6 利用运行一个时间步长的参数来计算下一时刻送风参数 （这里用到控制算法）
        '''
        # 计算控制算法和空调模型所需参数
        Tw[i] = t_HR_ts(ep_T[i], ep_HR[i] / 100)                # 计算湿球温度
        PMV[i] = get_PMV(ep_T[i],ep_RH[i])                      # 计算PMV
        Elec_params = get_electricity_price(step[i])                  # 调用函数获取目前电价信息
        Elec_price[i] = Elec_params[0]
        Elec_price1[i] = Elec_params[1]
        t[i] = Elec_params[2]
        t1[i] = Elec_params[3]
        if i == 0 :
            T_c[i] = ep_T[i] - T_ini                                # 计算温度变化率
            RH_c[i] = ep_RH[i] - RH_ini                             # 计算相对湿度变化率
            HR_c[i] = ep_HR[i] - HR_ini                             # 计算含湿量变化率
            PMV_c = PMV[i]                                          # 计算PMV变化率，设置PMV_ini = 0
            speed[i] = control_RL(ep_T_out[i], ep_HR_out[i], ep_Solar_direct[i], T_out_ini, ep_T[i], ep_HR[i], PMV[i],
                                  T_c[i], HR_c[i], PMV_c[i], C_ini, F_ini, Elec_price, Elec_price1, t, t1)
        else:
            T_c[i] = ep_T[i] - ep_T[i-1]        # 计算温度变化率
            RH_c[i] = ep_RH[i] - ep_RH[i-1]     # 计算相对湿度变化率
            HR_c[i] = ep_HR[i] - ep_HR[i-1]     # 计算含湿量变化率
            PMV_c = PMV[i] - PMV[i-1]           # 计算PMV变化率

            # 调用控制算法及空调模型(需要获取很多数据)
            speed[i] = control_RL(ep_T_out[i], ep_HR_out[i], ep_Solar_direct[i], T_out_ini, ep_T[i],ep_HR[i], PMV[i], T_c[i], HR_c[i], PMV_c[i], speed[i-1,0], speed[i-1,1], Elec_price, Elec_price1, t, t1)       # 可能需要float，[i,0]是因为要维度相同
        cooling_load[i] = cond(float(ep_T[i]), float(Tw[i]), speed[i, 0], speed[i, 1] / 1250 * 100)
        # 调用函数计算出送风数据
        y1 = 0.766956 + 0.0107756 * Tw[i] - 0.0000414703 * Tw[i] ** 2 + 0.00134961 * ep_T_out[i] - 0.000261144 * \
             ep_T_out[
                 i] ** 2 + 0.000457488 * Tw[i] * ep_T_out[i]
        supply_params = supply(ep_T[i], ep_HR[i], cooling_load[i])
        to_T_supply[i] = supply_params[0]
        to_HR_supply[i] = supply_params[1]
        to_m_supply[i] = supply_params[2]                # 风量固定0.3kg/s
        # 所有送风参数计算完后再加时间步长
        sim_start += step_time                           # sim_start这个参数必须要变化，因为do_step进行模拟需要这个参数每次变化一个step_time
        i += 1

    # 计算其他便于输出
    return ep_T, ep_HR, T_c, HR_c, 


    #%%
    '''
    7 画图 
    '''
    plt.plot(step, ep_T, label='T')
    plt.plot(step, ep_RH, label='RH')
    plt.show()

    #%%
    '''
    8 把验证数据等导入到excel表
    '''
    # 创建需要导出到Excel的参数字典
    dic = {'cooling_sensible': cooling_load[:,0],'ep_Qs_zone': ep_Qs_zone[:,0], 'ep_Qs_supplyair': ep_Qs_supplyair[:,0], } # [:,0]的意思是取第一列的所有行，把二维ndarray变成一维array，字典不能把键值对中的值value设成二维
    # 调用Excel_Export.py文件中的To_Excel函数，把数据导出到a.xlsx的excel文件中
    file_name = 'a.xlsx'                                          # file_name只有文件名就是在project里面生成excel
    # file_name = r"C:\Users\Bobby\Desktop\a.xlsx"                # 也可以放置到桌面上，必须要加r，选用a的原因是a.xlsx可以在project的最上面
    Excel_Export(dic,file_name)
