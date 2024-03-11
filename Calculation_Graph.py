# @Time    : 2024/2/18 16:08
# @Author  : Bobby Johnson
# @Project : Reinforcement Learning 
# @File    : 1
# @Software: PyCharm
# @Targets :
#%%
import torch
import torch.nn as nn
from torchviz import make_dot

class Actor(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 4)
        self.activation = nn.ReLU()
        self.fc2 = nn.Linear(4, 4)
        self.fc3 = nn.Linear(4, output_size)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, input):
        a = self.fc1(input)
        a = self.activation(a)
        a = self.fc2(a)
        a = self.activation(a)
        a = self.fc3(a)
        probability = self.softmax(a)
        return probability
# 以AlexNet为例，前向传播
x = torch.rand(2,2)
model = Actor(2,2)
y = model(x)

# 构造图对象，3种方式
# g = make_dot(y)
# g = make_dot(y, params=dict(model.named_parameters()))
g = make_dot(y, params=dict(list(model.named_parameters()) + [('x', x)]))

# 保存图像
g.view()  # 生成 Digraph.gv.pdf，并自动打开
# g.render(filename='graph', view=False)  # 保存为 graph.pdf，参数view表示是否打开pdf

torch.rand