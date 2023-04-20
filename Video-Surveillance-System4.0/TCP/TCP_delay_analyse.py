import csv
import matplotlib.pyplot as plt

# 将TCP各个时延数据读入
with open('TCP_delay.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    delay = [row[0] for row in reader]

with open('TCP_delay.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    img_delay = [row[1] for row in reader]

with open('TCP_delay.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    pack_delay = [row[2] for row in reader]

# 将字符串转化为浮点数
delay = list(map(float, delay))
img_delay = list(map(float, img_delay))
pack_delay = list(map(float, pack_delay))

# 创建图表对象并设置标题和坐标轴标签
plt.figure(figsize=(15, 8), dpi=100)

# 绘制折线图
plt.plot([i for i in range(100)], delay[:100], label='total_delay')
plt.plot([i for i in range(100)], img_delay[:100], label='encode_delay')
plt.plot([i for i in range(100)], pack_delay[:100], label='pack_delay')

# 生成图例并放置在右上角
plt.legend(loc='upper right')

# 添加标题和坐标轴标签
plt.title('TCP Delay Compare')
plt.xlabel('100Frame', loc='right')
plt.ylabel('Delay /s', loc='top')

# 显示图表
plt.show()