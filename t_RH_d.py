# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 20:50:29 2023

@author: Administrator
"""
import t_Pb
def t_RH_d(t,RH):
    """
    干球温度 + 相对湿度 ---> 含湿量
    :param t: 干球温度
    :param RH: 相对湿度
    :return d：含湿量
    """

    Pb=t_Pb.t_Pb(t)
    Pv=Pb*RH
    d=0.621945*Pv/(101325.0-Pv)
    return d