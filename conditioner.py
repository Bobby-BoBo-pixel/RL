# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 10:43:55 2023

@author: Administrator
"""

#%%

import numpy as np
import math
def cond(Td,Tw,C,F):
    """

    :param Td: 干球温度
    :param Tw: 湿球温度
    :param C: 压缩机频率
    :param F: 风机转速
    :return: CCs:显热冷量 ,CCl：潜热冷量
    """
    wi_h=np.mat([[0.41394516,-0.455535647,-0.234113546,0.308292756],[-0.491610979,0.308700082,0.069613063,1.094943061],         [0.120555124,-0.581965258,0.006108195,0.32445705],[-0.463566295,0.510484445,0.128116318,0.518575278],[-0.811678686,1.437834053,0.205923506,0.62169833],[-0.321145258,-0.504442733,-0.181597833,-0.116471731],[0.211912742,-0.932662303,0.035697898,-0.207291666],[-0.065482352,0.275862153,-0.339478737,-0.269242123],[0.47484868,-0.465657785,-0.200325776,-0.901494634],[-0.030803382,-0.098630293,0.655804217,-0.153891642]])
    bi_h=np.mat([[-0.486506925],[0.068057808],[-0.123019115],[1.235385076],[-1.653230028],[-0.561085158],[-0.636299708],[0.458925641],[-0.437985237],[0.736411878]])
    wh_o=np.mat([[0.581959608,-0.138866272,0.227167723,0.531144536,0.111155526,-0.327386958,0.199881725,-0.474388327,-0.076880567,0.50868937],[-0.784560647,-0.669429827,0.745029728,-0.591653163,1.074402066,-0.049340771,-0.730260311,0.179012856,-0.71492594,0.60036133]])
    bh_o=np.mat([[-0.533521993],[0.310591457]])
    input_max=np.mat([26.1107843400000,21.9510486800000,80,70])
    input_min=np.mat([21.9798694600000,16.8725499700000,30,30])
    # output_max=np.mat([5366.51813600000,3951.44064000000])
    output_max=np.mat([2700,2000])
    # output_min=np.mat([1609.92458500000,0])
    output_min=np.mat([800,0])
    a1=np.mat([[Td,Tw,C,F]])-input_min
    a2=input_max-input_min
    a3=np.divide(a1,a2)
    inputn=a3*2-1
    inputn=np.transpose(inputn)
    hi=wi_h*inputn+bi_h
    h_o=np.zeros((10,1))
    for i in range(10):
        h_o[i]=2/(math.exp(-2*hi[i])+1)-1
    out_h=wh_o*h_o+bh_o
    output=np.transpose(out_h)
    c1=(output+1)/2
    c2=np.multiply(c1,output_max-output_min)+output_min
    output=c2
    CCs=output[0,0]
    CC1=output[0,1]
    if(CCs<0):
        CCs=0
        
    if(CC1<0):
        CC1=0
    if(C==0 and F==0):
        CCs=0
        CC1=0
    return CCs,CC1 # 这里因为空调冷量太大，需要改小
a1=cond(26,17.1,60,50)
print(a1)