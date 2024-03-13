# @Time    : 2024/2/28 23:39
# @Author  : Bobby Johnson
# @Project : GuangZhou_FLC_Simplest.py
# @File    : Electricity
# @Software: PyCharm
# @Targets :

def get_electricity_price(step):
    t = step % 288           # 确定step是一天中的第几个step
    h = int(t / 12)          # 确定step是一天中第几个小时
    if h >= 7 and h < 8:
        price = 0.3784
        price1 = 0.9014
        t1 = 8*12 - t
    if h >=8 and h<11:
        price = 0.9014
        price1 = 0.3784
        t1 = 11*12 - t
    if h >=11 and h<13:
        price = 0.3784
        price1 = 1.2064
        t1 = 13*12 - t
    if h >=13 and h<15:
        price = 1.2064
        price1 = 0.9014
        t1 = 15*12 - t
    if h >=15 and h<=17:
        price = 0.9014
        price1 = 0.3784
        t1 = 17*12 - t
    return price, price1, t, t1
