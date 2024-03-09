# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 20:47:49 2023

@author: Administrator
"""
import t_RH_d
import t_d_ts
def t_RH_ts(t,RH):
    """
    干球温度+相对湿度 ---> 湿球温度
    :param t: 干球温度
    :param RH: 相对湿度
    :return:  ts：湿球温度
    """
    d=t_RH_d.t_RH_d(t,RH)
    ts=t_d_ts.t_d_ts(t,d)
    return ts
ts=t_RH_ts(25,0.3)