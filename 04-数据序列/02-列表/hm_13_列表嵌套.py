name_list = [['TOM', 'Lily', 'Rose'], ['张三', '李四', '王五'], ['xiaohong', 'xiaoming', 'xiaolv']]

# print(name_list)

# 列表嵌套的时候的数据查询
# print(name_list[0])
print(name_list[0][1])


# 列表嵌套遍历
for i in name_list:
    for j in i:
        print(f"{j}",end=" ")







