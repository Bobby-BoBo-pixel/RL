# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 20:53:51 2023

@author: Administrator
"""
import numpy as np
import math
def t_Pb(t):
    '''
    这个方程是要引用的(不用管是什么原理)
    :param t:干球温度
    :return Pb：饱和水蒸气分压力
    '''
    T=t+273.15
    if(t>-100 and t<0):
        c1=-5674.5359
        c2=6.3925247
        c3=-0.9677843*10^(-2)
        c4=0.62215701*10^(-6)
        c5=0.20747825*10^(-18)
        c6=-0.9484024*10^(-12)
        c7=4.1635019
        Temp=c1/T+c2+c3*T+c4*T^2+c5*T^3+c6*T^4+c7*np.log10(T)
    if(t>=0 and t<200):
        Temp=-5800.2206/T+1.3914993-4.8640239*np.power(10.0,-2.0)*T+4.1764768*np.power(10.0,-5.0)*np.power(T,2.0)-1.4452093*np.power(10.0,-8.0)*np.power(T,3.0)+6.5459673*np.log(T)
    Pb=math.exp(Temp)
    return Pb