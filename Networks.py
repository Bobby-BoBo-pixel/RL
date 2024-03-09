# @Time    : 2024/2/29 12:08
# @Author  : Bobby Johnson
# @Project : GuangZhou_FLC_Simplest.py
# @File    : Networks
# @Software: PyCharm
# @Targets : 创建策略和价值网络 Create Policy & Value Network

#%%
'''
1 建立神经网络
'''

import torch
import torch.nn as nn

# 定义模型

# 策略网络Actor类创建
class Actor(nn.Module):   # 继承自nn.Module父类, 每个自己建立的Network都要继承Module类
    def __init__(self, input_size, output_size):
        # super()方法引用父类__init__()方法，必须要引用，否则神经网络不能正确initialize
        super().__init__()
        # 第一个全连接层由Linear类实例化，并且此实例被赋值给了Actor类的一个类属性self.fc1 (fc: fully connected)
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 256)
        self.fc4 = nn.Linear(256, output_size)
        # 第一个激活层由ReLU类实例化.并且实例被赋值给了Actor类的一个类属性self.activation1
        self.activation1 = nn.ReLU()
        self.activation2 = nn.ReLU()
        self.activation3 = nn.ReLU()
        # softmax层实例化，把output_size转化为总和为1的概率
        self.softmax = nn.Softmax(dim=1)

    def forward(self, input):
        # self.fc1实例调用它的forward方法(实际上应该是Module父类的__call__方法)进行前向传播
        a = self.fc1(input)
        a = self.activation1(a)
        a = self.fc2(a)
        a = self.activation2(a)
        a = self.fc3(a)
        a = self.activation3(a)
        a = self.fc4(a)
        probs = self.softmax(a)
        return probs

# 价值网络Critic类
class Critic(nn.Module):            # 注释同Actor类一样
    def __init__(self, input_size, output_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 256)
        self.fc4 = nn.Linear(256, output_size)
        self.activation1 = nn.ReLU()
        self.activation2 = nn.ReLU()
        self.activation3 = nn.ReLU()

    def forward(self, input):
        a = self.fc1(input)
        a = self.activation1(a)
        a = self.fc2(a)
        a = self.activation2(a)
        a = self.fc3(a)
        a = self.activation3(a)
        value = self.fc4(a)
        return value

# 实例化Actor
model_action = Actor(16, 121)      # 输入input_size = 16, output_size = 121
model_value = Critic(16, 1)      # 输入input_size = 16, output_size = 1
# 创建两个网络输入
input_actor = torch.rand((2, 16))
input_critic = torch.rand((2, 16))
# 调用实例forward(__call__)方法进行网络前向传播
probs = model_action(input_actor)
value = model_value(input_critic)
# 两个网络前向传播结果输出
probs, value