import os

# 如果我们需要判断一个指定路径的文件或者目录是否存在，可以使用下面的方法
exists = os.path.exists("../15-文件和目录")
print(f"判断目录是否存在 exists = {exists}")

exists = os.path.exists("../15-文件和目录/1-创建目录.py")
print(f"判断文件是否存在 exists = {exists}")

# 如果你要判断指定路径是否是文件，可以这样
isfile = os.path.isfile("../15-文件和目录/1-创建目录.py")
print(f"判断指定路径是否是文件 isfile = {isfile}")

# 如果你要判断指定路径是否是目录，可以这样
isdir = os.path.isdir("../15-文件和目录/")
print(f"判断指定路径是否是目录 isdir = {isdir}")
