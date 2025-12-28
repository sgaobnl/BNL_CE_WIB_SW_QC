import matplotlib.pyplot as plt
import numpy as np

x = np.array([1,2,3,4,5,6,7,8])
y = np.array([2,4,5,6,7,8,9,12])

error = np.array([0.5, 0.3, 0.2, 0.3, 0.5, 0.4, 0.1, 0.6])

plt.errorbar(x, y, yerr = error, fmt = 'o', color='blue')

plt.xlabel('X-axis')
plt.ylabel('Y-axis')


plt.title('Data0')
plt.legend()

plt.show()