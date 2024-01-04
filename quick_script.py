import matplotlib.pyplot as plt
import numpy as np

# 生成一些示例数据
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.tan(x)
y4 = np.exp(-x)

# 创建一个2x2的subplot布局
plt.subplot(2, 2, 1)
plt.plot(x, y1)
plt.title('Plot 1')

plt.subplot(2, 2, 2)
plt.plot(x, y2)
plt.title('Plot 2')

plt.subplot(2, 2, 3)
plt.plot(x, y3)
plt.title('Plot 3')

plt.subplot(2, 2, 4)
plt.plot(x, y4)
plt.title('Plot 4')

# 调整布局
plt.tight_layout()

# 显示图形
plt.show()
