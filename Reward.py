# @Time    : 2024/2/28 23:49
# @Author  : Bobby Johnson
# @Project : GuangZhou_FLC_Simplest.py
# @File    : Reward
# @Software: PyCharm
# @Targets :

def Reward(PMV_t1, G_t):
    '''
    :param PMV_t1: t+1时刻的PMV
    :param G_t: t时刻的电费
    :return: reward: t时刻的回报/奖励
    '''
    if abs(PMV_t1) <= 0.5:
        reward = -50 * G_t
        return reward
    if abs(PMV_t1) > 0.5:
        reward = -50 * G_t - 100 * (PMV_t1 - 0.5)
        return reward
