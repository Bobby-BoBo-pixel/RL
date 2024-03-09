# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 10:30:15 2023

@author: Administrator
"""
def cont(T_t0,T_t1,RH_t0,RH_t1,C_t1,F_t1):
    """
    此文件是控制算法，给定参数，输出需要的压缩机、风机转速（对应自己的强化学习控制算法）
    :param T_t0: 上一时刻温度
    :param T_t1: 此时刻温度
    :param RH_t0: 上一时刻湿度
    :param RH_t1: 下一时刻湿度
    :param C_t1: 此时刻压缩机频率
    :param F_t1: 此时刻风机转速
    :return :C_t2：下一时刻压缩机频率      F_t2: 下一时刻风机转速
    """
    Fmin=500   #风机最小转速为500
    Fmax=1250  #风机最大转速为1250
    Cmin=20    #压缩机最小转速为20
    Cmax=90    #压缩机最大转速为90
    t0=10      #读取时间间隔为10s
    T0=25      #设定的温度值为25℃
    RH0=50     #设定的相对湿度为50%
    #温度误差比较值
    e5t=4
    e4t=2.5
    e3t=1
    e2t=0.5
    e1t=0.03
    #温度误差权重值设定
    a5t=4
    a4t=0.4
    a3t=0.1
    a2t=0.02
    a1t=0
    #温度误差变化率比较值
    f5t=3
    f4t=3
    f3t=3
    f2t=0.04
    f1t=0.01
#温度误差变化率权重值设定
    b5t=0.6
    b4t=0.6
    b3t=0.6
    b2t=0.16
    b1t=0.02
#相对湿度误差比较值
    e5r=12
    e4r=7
    e3r=4
    e2r=2
    e1r=1
#相对湿度误差权重值设定
    a5r=2.5
    a4r=1.2
    a3r=0.3
    a2r=0.02
    a1r=0.008
#相对湿度误差变化率比较值
    f5r=10
    f4r=8
    f3r=5
    f2r=3
    f1r=1
#相对湿度误差变化率权重值设定
    b5r=4
    b4r=0.6
    b3r=0.2
    b2r=0.1
    b1r=0.02
#变量名解释
#温度误差计算权重值e1,e21,e3
#温度误差变化率计算权重值ec1,ec21,ec3
#相对湿度误差计算权重值e22
#相对湿度误差变化率计算权重值ec22
#压缩机计算权重值c1,c22,c3
#风机计算权重值c21

    a1=(T_t1-T0)
    if(a1>2):
        F_t2=Fmax
        if(a1>e5t):
            e1=a5t
        if(a1>e4t and a1<=e5t):
            e1=(a1-e4t)/(e5t-e4t)*a5t+(e5t-a1)/(e5t-e4t)*a4t
        if(a1>e3t and a1<=e4t):
            e1=(a1-e3t)/(e4t-e3t)*a4t+(e4t-a1)/(e4t-e3t)*a3t
        if(a1>e2t and a1<=e3t):    
            e1=(a1-e2t)/(e3t-e2t)*a3t+(e3t-a1)/(e3t-e2t)*a2t
        if(a1>e1t and a1<=e2t):      
            e1=(a1-e1t)/(e2t-e1t)*a2t+(e2t-a1)/(e2t-e1t)*a1t
        if(a1>0 and a1<=e1t):       
            e1=(a1-0)/(e1t-0)*a1t+(e1t-a1)/(e1t-0)*0
        if(a1<-e5t):
            e1=-a5t
        if(a1<-e4t and a1>=-e5t):    
            e1=(a1-(-e4t))/(e5t-e4t)*a5t+((-e5t)-a1)/(e5t-e4t)*a4t 
        if(a1<-e3t and a1>=-e4t):    
            e1=(a1-(-e3t))/(e4t-e3t)*a4t+((-e4t)-a1)/(e4t-e3t)*a3t
        if(a1<-e2t and a1>=-e3t):    
            e1=(a1-(-e2t))/(e3t-e2t)*a3t+((-e3t)-a1)/(e3t-e2t)*a2t
        if(a1<-e1t and a1>=-e2t):    
            e1=(a1-(-e1t))/(e2t-e1t)*a2t+((-e2t)-a1)/(e2t-e1t)*a1t
        if(a1<=0 and a1>=-e1t):      
            e1=(a1-0)/(e1t-0)*a1t+((-e1t)-a1)/(e1t-0)*0
        b1=(T_t1-T_t0)*10   #温度误差变化率 单位为℃/min
        if(b1>f5t):
            ec1=b5t
        if(b1>f4t and b1<=f5t):       
            ec1=(b1-f4t)/(f5t-f4t)*b5t+(f5t-b1)/(f5t-f4t)*b4t
        if(b1>f3t and b1<=f4t):       
            ec1=(b1-f3t)/(f4t-f3t)*b4t+(f4t-b1)/(f4t-f3t)*b3t
        if(b1>f2t and b1<=f3t):       
            ec1=(b1-f2t)/(f3t-f2t)*b3t+(f3t-b1)/(f3t-f2t)*b2t
        if(b1>f1t and b1<=f2t):       
            ec1=(b1-f1t)/(f2t-f1t)*b2t+(f2t-b1)/(f2t-f1t)*b1t
        if(b1>0 and b1<=f1t):         
            ec1=(b1-0)/(f1t-0)*b1t+(f1t-b1)/(f1t-0)*0
        if(b1<-f5t):
            ec1=-b5t
        if(b1<-f4t and b1>=-f5t):     
            ec1=(b1-(-f4t))/(f5t-f4t)*b5t+((-f5t)-b1)/(f5t-f4t)*b4t
        if(b1<-f3t and b1>=-f4t):     
            ec1=(b1-(-f3t))/(f4t-f3t)*b4t+((-f4t)-b1)/(f4t-f3t)*b3t
        if(b1<-f2t and b1>=-f3t):     
            ec1=(b1-(-f2t))/(f3t-f2t)*b3t+((-f3t)-b1)/(f3t-f2t)*b2t
        if(b1<-f1t and b1>=-f2t):     
            ec1=(b1-(-f1t))/(f2t-f1t)*b2t+((-f2t)-b1)/(f2t-f1t)*b1t
        if(b1<=0 and b1>=-f1t):       
            ec1=(b1-0)/(f1t-0)*b1t+((-f1t)-b1)/(f1t-0)*0
        c1=e1+ec1
        if(c1<0):
            C_t2=C_t1+(C_t1-Cmin)*c1/(a5t+b5t)
        else:
            C_t2=C_t1+(Cmax-C_t1)*c1/(a5t+b5t)   #Z(t+1)为下一时刻的压缩机转速设定值
    if(a1>=-2 and a1<=2):
        a1=a1*10
        if(a1>e5t):
            e21=a5t
        if(a1>e4t and a1<=e5t):
            e21=(a1-e4t)/(e5t-e4t)*a5t+(e5t-a1)/(e5t-e4t)*a4t
        if(a1>e3t and a1<=e4t):
            e21=(a1-e3t)/(e4t-e3t)*a4t+(e4t-a1)/(e4t-e3t)*a3t
        if(a1>e2t and a1<=e3t):
            e21=(a1-e2t)/(e3t-e2t)*a3t+(e3t-a1)/(e3t-e2t)*a2t
        if(a1>e1t and a1<=e2t):
            e21=(a1-e1t)/(e2t-e1t)*a2t+(e2t-a1)/(e2t-e1t)*a1t
        if(a1>0 and a1<=e1t):
            e21=(a1-0)/(e1t-0)*a1t+(e1t-a1)/(e1t-0)*0
        if(a1<-e5t):
            e21=-a5t
        if(a1<-e4t and a1>=-e5t):
            e21=(a1-(-e4t))/(e5t-e4t)*a5t+((-e5t)-a1)/(e5t-e4t)*a4t
        if(a1<-e3t and a1>=-e4t):
            e21=(a1-(-e3t))/(e4t-e3t)*a4t+((-e4t)-a1)/(e4t-e3t)*a3t
        if(a1<-e2t and a1>=-e3t):
            e21=(a1-(-e2t))/(e3t-e2t)*a3t+((-e3t)-a1)/(e3t-e2t)*a2t
        if(a1<-e1t and a1>=-e2t):
            e21=(a1-(-e1t))/(e2t-e1t)*a2t+((-e2t)-a1)/(e2t-e1t)*a1t
        if(a1<=0 and a1>=-e1t):
            e21=(a1-0)/(e1t-0)*a1t+((-e1t)-a1)/(e1t-0)*0
        b1=(T_t1-T_t0)*100
        if(b1>f5t):
            ec21=b5t
        if(b1>f4t and b1<=f5t):       
            ec21=(b1-f4t)/(f5t-f4t)*b5t+(f5t-b1)/(f5t-f4t)*b4t
        if(b1>f3t and b1<=f4t):       
            ec21=(b1-f3t)/(f4t-f3t)*b4t+(f4t-b1)/(f4t-f3t)*b3t
        if(b1>f2t and b1<=f3t):       
            ec21=(b1-f2t)/(f3t-f2t)*b3t+(f3t-b1)/(f3t-f2t)*b2t
        if(b1>f1t and b1<=f2t):       
            ec21=(b1-f1t)/(f2t-f1t)*b2t+(f2t-b1)/(f2t-f1t)*b1t
        if(b1>0 and b1<=f1t):         
            ec21=(b1-0)/(f1t-0)*b1t+(f1t-b1)/(f1t-0)*0
        if(b1<-f5t):
            ec21=-b5t
        if(b1<-f4t and b1>=-f5t):     
            ec21=(b1-(-f4t))/(f5t-f4t)*b5t+((-f5t)-b1)/(f5t-f4t)*b4t
        if(b1<-f3t and b1>=-f4t):     
            ec21=(b1-(-f3t))/(f4t-f3t)*b4t+((-f4t)-b1)/(f4t-f3t)*b3t
        if(b1<-f2t and b1>=-f3t):     
            ec21=(b1-(-f2t))/(f3t-f2t)*b3t+((-f3t)-b1)/(f3t-f2t)*b2t
        if(b1<-f1t and b1>=-f2t):     
            ec21=(b1-(-f1t))/(f2t-f1t)*b2t+((-f2t)-b1)/(f2t-f1t)*b1t
        if(b1<=0 and b1>=-f1t):       
            ec21=(b1-0)/(f1t-0)*b1t+((-f1t)-b1)/(f1t-0)*0
        c21=e21+ec21
        if(c21<0):
            F_t2=F_t1+(F_t1-Fmin)*c21/(a5t+b5t)
        if(c21>=0):
            F_t2=F_t1+(Fmax-F_t1)*c21/(a5t+b5t)
        a2=(RH_t1-RH0)*10
        if(a2>e5r):
            e22=a5r
        if(a2>e4r and a2<=e5r):
            e22=(a2-e4r)/(e5r-e4r)*a5r+(e5r-a2)/(e5r-e4r)*a4r
        if(a2>e3r and a2<=e4r):
            e22=(a2-e3r)/(e4r-e3r)*a4r+(e4r-a2)/(e4r-e3r)*a3r
        if(a2>e2r and a2<=e3r):
            e22=(a2-e2r)/(e3r-e2r)*a3r+(e3r-a2)/(e3r-e2r)*a2r
        if(a2>e1r and a2<=e2r):      
            e22=(a2-e1r)/(e2r-e1r)*a2r+(e2r-a2)/(e2r-e1r)*a1r
        if(a2>0 and a2<=e1r):        
            e22=(a2-0)/(e1r-0)*a1r+(e1r-a2)/(e1r-0)*0
        if(a2<-e5r):
            e22=-a5r
        if(a2<-e4r and a2>=-e5r):    
            e22=(a2-(-e4r))/(e5r-e4r)*a5r+((-e5r)-a2)/(e5r-e4r)*a4r
        if(a2<-e3r and a2>=-e4r):    
            e22=(a2-(-e3r))/(e4r-e3r)*a4r+((-e4r)-a2)/(e4r-e3r)*a3r
        if(a2<-e2r and a2>=-e3r):    
            e22=(a2-(-e2r))/(e3r-e2r)*a3r+((-e3r)-a2)/(e3r-e2r)*a2r
        if(a2<-e1r and a2>=-e2r):    
            e22=(a2-(-e1r))/(e2r-e1r)*a2r+((-e2r)-a2)/(e2r-e1r)*a1r
        if(a2<=0 and a2>=-e1r):     
            e22=(a2-0)/(e1r-0)*a1r+((-e1r)-a2)/(e1r-0)*0
        b2=(RH_t1-RH_t0)*10   #相对湿度误差变化率 单位为%/min
        if(b2>f5r):
            ec22=b5r
        if (b2>f4r and b2<=f5r):       
            ec22=(b2-f4r)/(f5r-f4r)*b5r+(f5r-b2)/(f5r-f4r)*b4r
        if (b2>f3r and b2<=f4r):       
            ec22=(b2-f3r)/(f4r-f3r)*b4r+(f4r-b2)/(f4r-f3r)*b3r
        if (b2>f2r and b2<=f3r):       
            ec22=(b2-f2r)/(f3r-f2r)*b3r+(f3r-b2)/(f3r-f2r)*b2r
        if (b2>f1r and b2<=f2r):       
            ec22=(b2-f1r)/(f2r-f1r)*b2r+(f2r-b2)/(f2r-f1r)*b1r
        if (b2>0 and b2<=f1r):         
            ec22=(b2-0)/(f1r-0)*b1r+(f1r-b2)/(f1r-0)*0
        if(b2<-f5r):
            ec22=-b5r
        if(b2<-f4r and b2>=-f5r):     
            ec22=(b2-(-f4r))/(f5r-f4r)*b5r+((-f5r)-b2)/(f5r-f4r)*b4r
        if(b2<-f3r and b2>=-f4r):     
            ec22=(b2-(-f3r))/(f4r-f3r)*b4r+((-f4r)-b2)/(f4r-f3r)*b3r
        if(b2<-f2r and b2>=-f3r):     
            ec22=(b2-(-f2r))/(f3r-f2r)*b3r+((-f3r)-b2)/(f3r-f2r)*b2r
        if(b2<-f1r and b2>=-f2r):    
            ec22=(b2-(-f1r))/(f2r-f1r)*b2r+((-f2r)-b2)/(f2r-f1r)*b1r
        if(b2<=0 and b2>=-f1r):       
            ec22=(b2-0)/(f1r-0)*b1r+((-f1r)-b2)/(f1r-0)*0
        c22=e22+ec22
        if(c22<0):
            C_t2=C_t1+(C_t1-Cmin)*c22/(a5r+b5r)
        if(c22>=0):
            C_t2=C_t1+(Cmax-C_t1)*c22/(a5r+b5r)  #Z(t+1)为下一时刻的压缩机转速设定值
    if(a1<-2):
        a1=a1
        F_t2=Fmin
        if(a1>e5t):
            e3=a5t
        if(a1>e4t and a1<=e5t):      
          e3=(a1-e4t)/(e5t-e4t)*a5t+(e5t-a1)/(e5t-e4t)*a4t
        if(a1>e3t and a1<=e4t):      
          e3=(a1-e3t)/(e4t-e3t)*a4t+(e4t-a1)/(e4t-e3t)*a3t
        if(a1>e2t and a1<=e3t):     
          e3=(a1-e2t)/(e3t-e2t)*a3t+(e3t-a1)/(e3t-e2t)*a2t  
        if(a1>e1t and a1<=e2t):      
          e3=(a1-e1t)/(e2t-e1t)*a2t+(e2t-a1)/(e2t-e1t)*a1t
        if(a1>0 and a1<=e1t):        
          e3=(a1-0)/(e1t-0)*a1t+(e1t-a1)/(e1t-0)*0
        if(a1<-e5t):
          e3=-a5t
        if(a1<-e4t and a1>=-e5t):    
          e3=(a1-(-e4t))/(e5t-e4t)*a5t+((-e5t)-a1)/(e5t-e4t)*a4t
        if(a1<-e3t and a1>=-e4t):    
          e3=(a1-(-e3t))/(e4t-e3t)*a4t+((-e4t)-a1)/(e4t-e3t)*a3t
        if(a1<-e2t and a1>=-e3t):    
          e3=(a1-(-e2t))/(e3t-e2t)*a3t+((-e3t)-a1)/(e3t-e2t)*a2t
        if(a1<-e1t and a1>=-e2t):    
          e3=(a1-(-e1t))/(e2t-e1t)*a2t+((-e2t)-a1)/(e2t-e1t)*a1t
        if(a1<=0 and a1>=-e1t):      
          e3=(a1-0)/(e1t-0)*a1t+((-e1t)-a1)/(e1t-0)*0
        b1=(T_t1-T_t0)  #温度误差变化率 单位为℃/min
        if(b1>f5t):
          ec3=b5t
        if(b1>f4t and b1<=f5t):       
          ec3=(b1-f4t)/(f5t-f4t)*b5t+(f5t-b1)/(f5t-f4t)*b4t
        if(b1>f3t and b1<=f4t):       
          ec3=(b1-f3t)/(f4t-f3t)*b4t+(f4t-b1)/(f4t-f3t)*b3t
        if(b1>f2t and b1<=f3t):       
          ec3=(b1-f2t)/(f3t-f2t)*b3t+(f3t-b1)/(f3t-f2t)*b2t
        if(b1>f1t and b1<=f2t):       
          ec3=(b1-f1t)/(f2t-f1t)*b2t+(f2t-b1)/(f2t-f1t)*b1t
        if(b1>0 and b1<=f1t):         
          ec3=(b1-0)/(f1t-0)*b1t+(f1t-b1)/(f1t-0)*0
        if(b1<-f5t):
          ec3=-b5t
        if(b1<-f4t and b1>=-f5t):     
          ec3=(b1-(-f4t))/(f5t-f4t)*b5t+((-f5t)-b1)/(f5t-f4t)*b4t
        if(b1<-f3t and b1>=-f4t):     
          ec3=(b1-(-f3t))/(f4t-f3t)*b4t+((-f4t)-b1)/(f4t-f3t)*b3t
        if(b1<-f2t and b1>=-f3t):
          ec3=(b1-(-f2t))/(f3t-f2t)*b3t+((-f3t)-b1)/(f3t-f2t)*b2t
        if(b1<-f1t and b1>=-f2t):
          ec3=(b1-(-f1t))/(f2t-f1t)*b2t+((-f2t)-b1)/(f2t-f1t)*b1t
        if(b1<=0 and b1>=-f1t):
          ec3=(b1-0)/(f1t-0)*b1t+((-f1t)-b1)/(f1t-0)*0
        c3=e3+ec3
        if(c3<0):
          C_t2=C_t1+(C_t1-Cmin)*c3/(a5t+b5t)
        if(c3>=0):
          C_t2=C_t1+(Cmax-C_t1)*c3/(a5t+b5t)   #Z(t+1)为下一时刻的压缩机转速设定值
    return C_t2, F_t2
# def mode2(t+1):
# a1=T(t)-T0      #当前温度与设定温度的差值
# if(a1>e5t):
#      e21=a5t
#      else if (a1>e4t & a1<=e5t):      
#          e21=(a1-e4t)/(e5t-e4t)*a5t+(e5t-a1)/(e5t-e4t)*a4t
#      else if (a1>e3t & a1<=e4t):      
#          e21=(a1-e3t)/(e4t-e3t)*a4t+(e4t-a1)/(e4t-e3t)*a3t
#      else if (a1>e2t & a1<=e3t):      
#          e21=(a1-e2t)/(e3t-e2t)*a3t+(e3t-a1)/(e3t-e2t)*a2t
#      else if (a1>e1t & a1<=e2t):      
#          e21=(a1-e1t)/(e2t-e1t)*a2t+(e2t-a1)/(e2t-e1t)*a1t
#      else if (a1>0 & a1<=e1t):        
#          e21=(a1-0)/(e1t-0)*a1t+(e1t-a1)/(e1t-0)*0
# else if(a1<-e5t):
#      e21=-a5t
#      else if (a1<-e4t & a1>=-e5t):    
#          e21=(a1-(-e4t))/(e5t-e4t)*a5t+((-e5t)-a1)/(e5t-e4t)*a4t 
#      else if (a1<-e3t & a1>=-e4t):    
#          e21=(a1-(-e3t))/(e4t-e3t)*a4t+((-e4t)-a1)/(e4t-e3t)*a3t
#      else if (a1<-e2t & a1>=-e3t):    
#          e21=(a1-(-e2t))/(e3t-e2t)*a3t+((-e3t)-a1)/(e3t-e2t)*a2t
#      else if (a1<-e1t & a1>=-e2t):    
#          e21=(a1-(-e1t))/(e2t-e1t)*a2t+((-e2t)-a1)/(e2t-e1t)*a1t
#      else if (a1<=0 & a1>=-e1t):      
#          e21=(a1-0)/(e1t-0)*a1t+((-e1t)-a1)/(e1t-0)*0

# b1=(T(t)-T(t-1))/t0*60   #温度误差变化率 单位为℃/min
# if(b1>f5t):
#      ec21=b5t
#      else if (b1>f4t & b1<=f5t):       
#          ec21=(b1-f4t)/(f5t-f4t)*b5t+(f5t-b1)/(f5t-f4t)*b4t
#      else if (b1>f3t & b1<=f4t):       
#          ec21=(b1-f3t)/(f4t-f3t)*b4t+(f4t-b1)/(f4t-f3t)*b3t
#      else if (b1>f2t & b1<=f3t):       
#          ec21=(b1-f2t)/(f3t-f2t)*b3t+(f3t-b1)/(f3t-f2t)*b2t
#      else if (b1>f1t & b1<=f2t):       
#          ec21=(b1-f1t)/(f2t-f1t)*b2t+(f2t-b1)/(f2t-f1t)*b1t
#      else if (b1>0 & b1<=f1t):         
#          ec21=(b1-0)/(f1t-0)*b1t+(f1t-b1)/(f1t-0)*0
# else if(b1<-f5t):
#      ec21=-b5t
#      else if (b1<-f4t & b1>=-f5t):     
#          ec21=(b1-(-f4t))/(f5t-f4t)*b5t+((-f5t)-b1)/(f5t-f4t)*b4t
#      else if (b1<-f3t & b1>=-f4t):     
#          ec21=(b1-(-f3t))/(f4t-f3t)*b4t+((-f4t)-b1)/(f4t-f3t)*b3t
#      else if (b1<-f2t & b1>=-f3t):     
#          ec21=(b1-(-f2t))/(f3t-f2t)*b3t+((-f3t)-b1)/(f3t-f2t)*b2t
#      else if (b1<-f1t & b1>=-f2t):     
#          ec21=(b1-(-f1t))/(f2t-f1t)*b2t+((-f2t)-b1)/(f2t-f1t)*b1t
#      else if (b1<=0 & b1>=-f1t):       
#          ec21=(b1-0)/(f1t-0)*b1t+((-f1t)-b1)/(f1t-0)*0
#  c21=e21+ec21
#  if(c21<0):
#      Y(t+1)=Y(t)+(Y(t)-Ymin)*c21/(a5t+b5t)
#  else:
#      Y(t+1)=Y(t)+(Ymax-Y(t))*c21/(a5t+b5t)  #Y(t+1)为下一时刻的风机转速设定值

# a2=RH(t)-RH0      #当前相对湿度与设定相对湿度的差值
# if(a2>e5r):
#      e22=a5r
#      else if (a2>e4r & a2<=e5r):      
#          e22=(a2-e4r)/(e5r-e4r)*a5r+(e5r-a2)/(e5r-e4r)*a4r
#      else if (a2>e3r & a2<=e4r):      
#         e22=(a2-e3r)/(e4r-e3r)*a4r+(e4r-a2)/(e4r-e3r)*a3r 
#      else if (a2>e2r & a2<=e3r):      
#          e22=(a2-e2r)/(e3r-e2r)*a3r+(e3r-a2)/(e3r-e2r)*a2r
#      else if (a2>e1r & a2<=e2r):      
#          e22=(a2-e1r)/(e2r-e1r)*a2r+(e2r-a2)/(e2r-e1r)*a1r
#      else if (a2>0 & a2<=e1r):        
#          e22=(a2-0)/(e1r-0)*a1r+(e1r-a2)/(e1r-0)*0
# else if(a2<-e5r):
#      e22=-a5r
#      else if (a2<-e4r & a2>=-e5r):    
#          e22=(a2-(-e4r))/(e5r-e4r)*a5r+((-e5r)-a2)/(e5r-e4r)*a4r
#      else if (a2<-e3r & a2>=-e4r):    
#          e22=(a2-(-e3r))/(e4r-e3r)*a4r+((-e4r)-a2)/(e4r-e3r)*a3r
#      else if (a2<-e2r & a2>=-e3r):    
#          e22=(a2-(-e2r))/(e3r-e2r)*a3r+((-e3r)-a2)/(e3r-e2r)*a2r
#      else if (a2<-e1r & a2>=-e2r):    
#          e22=(a2-(-e1r))/(e2r-e1r)*a2r+((-e2r)-a2)/(e2r-e1r)*a1r
#      else if (a2<=0 & a2>=-e1r):     
#           e22=(a2-0)/(e1r-0)*a1r+((-e1r)-a2)/(e1r-0)*0

# b2=(RH(t)-RH(t-1))/t0*60   #相对湿度误差变化率 单位为%/min
# if(b2>f5r)
#      ec22=b5r
#      else if (b2>f4r & b2<=f5r):       
#          ec22=(b2-f4r)/(f5r-f4r)*b5r+(f5r-b2)/(f5r-f4r)*b4r
#      else if (b2>f3r & b2<=f4r):       
#          ec22=(b2-f3r)/(f4r-f3r)*b4r+(f4r-b2)/(f4r-f3r)*b3r
#      else if (b2>f2r & b2<=f3r):       
#          ec22=(b2-f2r)/(f3r-f2r)*b3r+(f3r-b2)/(f3r-f2r)*b2r
#      else if (b2>f1r & b2<=f2r):       
#          ec22=(b2-f1r)/(f2r-f1r)*b2r+(f2r-b2)/(f2r-f1r)*b1r
#      else if (b2>0 & b2<=f1r):         
#          ec22=(b2-0)/(f1r-0)*b1r+(f1r-b2)/(f1r-0)*0
# else if(b2<-f5r)
#      ec22=-b5r
#      else if (b2<-f4r & b2>=-f5r):     
#          ec22=(b2-(-f4r))/(f5r-f4r)*b5r+((-f5r)-b2)/(f5r-f4r)*b4r
#      else if (b2<-f3r & b2>=-f4r):     
#          ec22=(b2-(-f3r))/(f4r-f3r)*b4r+((-f4r)-b2)/(f4r-f3r)*b3r
#      else if (b2<-f2r & b2>=-f3r):     
#          ec22=(b2-(-f2r))/(f3r-f2r)*b3r+((-f3r)-b2)/(f3r-f2r)*b2r
#      else if (b2<-f1r & b2>=-f2r):    
#          ec22=(b2-(-f1r))/(f2r-f1r)*b2r+((-f2r)-b2)/(f2r-f1r)*b1r
#      else if (b2<=0 & b2>=-f1r):       
#         ec22=(b2-0)/(f1r-0)*b1r+((-f1r)-b2)/(f1r-0)*0

#  c22=e22+ec22
#  if(c22<0):
#      Z(t+1)=Z(t)+(Z(t)-Zmin)*c22/(a5r+b5r)
#  else:
#      Z(t+1)=Z(t)+(Zmax-Z(t))*c22/(a5r+b5r)  #Z(t+1)为下一时刻的压缩机转速设定值
     
#      return (Y(t+1),Z(t+1))


















