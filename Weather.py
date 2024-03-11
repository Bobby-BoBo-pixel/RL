# @Time    : 2024/3/4 15:51
# @Author  : Bobby Johnson
# @Project : GuangZhou_FLC_Simplest.py
# @File    : Weather
# @Software: PyCharm
# @Targets : 对天气进行spline三次方插值

#%%

from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def get_weather():
    '''
    不需要参数传递
    :return: T_spline, RH_spline, Solar_spline插值后的数据，size = [num,1]
    '''
    # 读取Excel文件
    # 确认文件所在路径
    path = 'F:\Onedrive\OneDrive - zju.edu.cn\Sync\Python_Project\Reinforcement Learning\RL\EnergyPlus_Python\GuangZhou_RL\GuangZhou_Weather_EP.xlsx'
    df = pd.read_excel(io=path)  # 如果Excel文件没有标题行，则设置header=None
    # 从DataFrame中提取所需的数据前5整列的数据（所有行）
    data = df.iloc[:,:5]
    # 将数据转换为NumPy数组
    array_data = np.array(data)
    # T为第1列，RH为第2列，Solar为第4列
    T = array_data[:,1]
    RH = array_data[:,2]
    Solar = array_data[:,4]
    # 统计共有多少个数据
    num = len(T)
    # t为横轴，保证横轴的个数和纵轴保持一致
    t = np.linspace(1,num,num)
    # CubicSpline类进行实例化
    cs_T = CubicSpline(t, T)
    cs_RH = CubicSpline(t,RH)
    cs_Solar = CubicSpline(t,Solar)
    # 在原始数据点之间创建一些新的数据点
    t_spline = np.linspace(1, num, num*12)
    # CubicSpline实例调用__call__方法进行插值计算
    T_spline = cs_T(t_spline)
    RH_spline = cs_RH(t_spline)
    Solar_spline = cs_Solar(t_spline)
    return T_spline, RH_spline, Solar_spline

# t, t_spline, RH, T_spline, RH_spline, Solar_spline = weather()
# # 绘制原始数据点和插值曲线
# plt.figure(figsize=(8, 6))
# plt.scatter(t, RH, color='red', label='Original Data')                         # 散点标出小时数，也就是原来没有进行插值的数据
# plt.plot(t_spline, RH_spline, color='blue', label='Cubic Spline Interpolation')      # plot拟合出插值后的曲线
# plt.xlabel('X')                               # 画出X/Y的label标题
# plt.ylabel('Y')
# plt.title('Cubic Spline Interpolation')       # 画出Title
# plt.legend()                                  # 画出Legend图例
# plt.grid(True)                                # 带网格
# plt.show()                                    # 展示出图
