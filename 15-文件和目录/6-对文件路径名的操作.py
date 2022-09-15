import os

# 对于文件名的操作，比如 获取文件名称，文件所在目录，文件路径的拼接等，都可以使用 os.path 模块。
# 通常我们喜欢使用格式化字符串的方法来做文件路径的拼接，但是如果你的程序需要在Linux、Windows等多个平台运行，
# 它们的路径的分隔符是不同的，Windows上是 \ , 而 Linux上是 /。
# 这时，我们应该使用 os.path 模块。 它能够自动处理类似 Data/data.csv 和 Data\data.csv 这样的文件路径差异。

path = '15-文件和目录/1-创建目录.py'

# 获取路径中的文件名部分 ===>1-创建目录.py
fileName = os.path.basename(path)
print("fileName = " + fileName)

# 获取路径中的目录部分---->15-文件和目录
dirPath = os.path.dirname(path)
print("dirPath = " + dirPath)

# 文件路径的拼接 =====>15-文件和目录/1-创建目录.py
path_join = os.path.join(dirPath, fileName)
print("path_join1 = " + path_join)

# 文件路径的拼接 =====>temp/data/adb/1-创建目录.py
path_join2 = os.path.join("temp", "data", "adb", os.path.basename(fileName))
print("path_join2 = " + path_join2)
