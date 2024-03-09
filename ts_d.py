# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 10:30:15 2023

@author: Administrator
"""
import t_Pb
def ts_d(ts):
    """
    湿球温度 ---> 含湿量
    :param ts: 湿球温度
    :return: ds：含湿量
    """
    ds=(0.621945*t_Pb.t_Pb(ts))/(101325.0-t_Pb.t_Pb(ts))
    return ds