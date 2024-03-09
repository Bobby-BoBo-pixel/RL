# @Time    : 2024/2/28 23:39
# @Author  : Bobby Johnson
# @Project : GuangZhou_FLC_Simplest.py
# @File    : Electricity
# @Software: PyCharm
# @Targets :

def scheme(t):
    if t >= 7 and t < 8:
        price = 0.3784
    if t >=8 and t<11:
        price = 0.9014
    if t >=11 and t<13:
        price = 0.3784
    if t >=13 and t<15:
        price = 1.2064
    if t >=15 and t<=17:
        price = 0.9014
    return price
