# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 10:22:01 2023

@author: Administrator
"""
import ts_d
def t_d_ts(t,d):
    '''
    干球温度+含湿量 ---> 湿球温度
    :param t:干球温度
    :param d:含湿量
    :return: twb:湿球温度
    '''
    twb_up=30
    twb_down=0
    twb_mid=(twb_down+twb_up)/2
    twb=0
    while abs(twb_mid-twb)>0.0001:
        twb_mid=(twb_down+twb_up)/2
        twb=(d*(2501+1.86*t)-2501*ts_d.ts_d(twb_mid)+1.006*t)/(4.186*d-2.326*ts_d.ts_d(twb_mid)+1.006)
        if twb>twb_mid:
         twb_down=twb_mid
        else:
         twb_up=twb_mid
    return twb