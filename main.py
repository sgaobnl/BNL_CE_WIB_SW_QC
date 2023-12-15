# main.py

import subprocess

# 定义要执行的 Python 文件的路径
file_to_execute = 'a.py'

# 使用 subprocess.run 调用 Python 文件，捕获标准输出
result = subprocess.run(['python', file_to_execute], capture_output=True, text=True)
print(result)
# 获取子脚本的输出
output_from_child = result.stdout.strip()  # 使用 strip() 移除可能的换行符

# 解析子脚本输出中的参数值
x, y, z = output_from_child.split()

# 打印子脚本的输出
print("x:", x)
print("y:", y)
print("z:", z)
