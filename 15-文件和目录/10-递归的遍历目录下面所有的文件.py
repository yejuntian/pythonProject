import os

# 使用 os库中的walk()方法获取某个目录中所有的文件，包括子目录里面的文件。

# 比如我们要得到某个目录下面所有的子目录 和所有的文件，存放在两个列表中

# 目标目录
targetDir = "../../pythonProject"
dp = []
files = []
dirs = []
pathList = []

# 下面的三个变量 dirpath, dirnames, filenames
# dirpath 代表当前遍历到的目录名
# dirnames 是列表对象，存放当前dirpath中的所有子目录名
# filenames 是列表对象，存放当前dirpath中的所有文件名
for (dirpath, dirnames, filenames) in os.walk(targetDir):
    dp.append(dirpath)
    dirs.extend(dirnames)
    files.extend(filenames)
    # 如果要得到某个目录下所有文件的全路径可以这样
    for file in filenames:
        path = os.path.join(dirpath, file)
        pathList.append(path)
print("-" * 10 + "所有目录名" + "-" * 10)
print(dp)
print("-" * 10 + "所有子目录名" + "-" * 10)
print(dirs)
print("-" * 10 + "所有文件名" + "-" * 10)
print(files)
print("-" * 10 + "所有文件全路径" + "-" * 10)
print(pathList)
