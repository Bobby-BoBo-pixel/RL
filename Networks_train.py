# @Time    : 2024/2/29 15:06
# @Author  : Bobby Johnson
# @Project : GuangZhou_FLC_Simplest.py
# @File    : Network_train
# @Software: PyCharm
# @Targets :


#%%

import torch
import torch.nn as nn
# 导入两个神经网络实例
from Networks import model_action, model_value
state = 1
reward = 1
next_state = 1
gamma = 0.98
lamda = 0.95
action = 1
# 创建优化器
optimizer_action = torch.optim.Adam(model_action.parameters(), lr=1e-3)
optimizer_value = torch.optim.Adam(model_value.parameters(), lr=1e-2)

# 设置require_grad函数来设置神经网络是否需要梯度
def requires_grad(model, model_value):
    for param in model.parameters():
        param.requires_grad_(model_value)

#%%
def train_value(state, reward, next_state):
    requires_grad(model_value, True)
    requires_grad(model_action, False)
    # 计算TD Target
    with torch.no_grad():
        v_t1 = model_value(next_state)
    y_t = reward + gamma*v_t1

    # 每批数据训练10次
    for _ in range(10):
        v_t = model_value(state)
        loss = nn.MSELoss(v_t, y_t)
        loss.backward()
        optimizer_value.step()
        optimizer_value.zero_grad()
    delta_t = v_t - y_t

    return delta_t.detach()

delta_t = train_value(state, reward, next_state)

#%%
def train_action(state, model_action, delta_t):
    requires_grad(model_action, True)
    requires_grad(model_value, False)
    # 计算GAE
    GAE = []
    for i in range(len(delta_t)):
        s = 0
        for j in range(i, len(delta_t)):
            s += delta_t[j]*(gamma*lamda)**(j-i)
        GAE.append(s)
    delta_t = torch.FloatTensor(delta_t).reshape(-1,1)
    # 策略网络前向传播： 计算旧参数
    with torch.no_grad():
        probs_old = model_action(state).gather(dim = 1, index = action)

    # 数据反复训练10次
    for _ in range(10):
        # 计算新参数
        probs_new = model_action(state).gather(dim = 1, index = action)
        # 求出概率变化：
        ratio = probs_new/probs_old
        # 计算截断的/和不截断的两个loss，取最小的
        surr1 = ratio*GAE                           # 不截断
        surr2 = ratio.clamp(0.8,1.2)*delta_t        # 截断，对ratio矩阵的所有元素进行限制，不得超出0.8-1.2的范围
        loss = -torch.min(surr1,surr2).mean()

        # 更新参数
        loss.backward()
        optimizer_action.step()
        optimizer_action.zero_grad()

    return loss.item()
train_action(state, action, delta_t)

#%%
def train():
    model_value.train()
    model_action.train()
    #
    for epoch in range(1000):
        steps = 0
        while steps< 200:













