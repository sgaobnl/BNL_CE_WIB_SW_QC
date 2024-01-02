# 示例字典
my_dict = {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3"
}

# 创建一个Markdown格式的表格
markdown_table = "| 键   | 值      |\n|------|---------|\n"

# 将字典的键和值拼接成一行，添加到表格中
for key, value in my_dict.items():
    markdown_table += f"| {key} | {value} |\n"

# 输出Markdown表格
print(markdown_table)
