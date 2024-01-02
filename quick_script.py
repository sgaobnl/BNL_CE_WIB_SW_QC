import copy

original_dict = {'key1': [1, 2, 3], 'key2': {'inner_key': 'value'}}

# 使用 deepcopy 创建字典的深拷贝
copied_dict = copy.deepcopy(original_dict)

# 修改原始字典的值
original_dict['key1'][0] = 100
original_dict['key2']['inner_key'] = 'updated_value'

# 打印深拷贝后的字典，观察是否受到原始字典的更改影响
print(copied_dict)
