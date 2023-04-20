import csv
import matplotlib.pyplot as plt

# 写入UDP和TCP时延数据
with open('UDP_delay.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    UDP_delay = [row[0] for row in reader]
with open('TCP_delay.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    TCP_delay = [row[0] for row in reader]

# 将字符串转化为浮点数
UDP_delay = list(map(float, UDP_delay))
TCP_delay = list(map(float, TCP_delay))

# 创建图表对象并设置标题和坐标轴标签
plt.figure(figsize=(15, 8), dpi=100)

# 绘制折线图
plt.plot([i for i in range(100)], UDP_delay[:100], label='UDP')
plt.plot([i for i in range(100)], TCP_delay[:100], label='TCP')

# 生成图例并放置在右上角
plt.legend(loc='upper right')

# 添加标题和坐标轴标签
plt.title('UDP-TCP Delay Compare')
plt.xlabel('100Frame', loc='right')
plt.ylabel('Delay /s', loc='top')

# 显示图表
plt.show()

