import os

# 目标目录
targetDir = "../workSpace"

# listdir返回的是该目录下面所有的文件和子目录
files = os.listdir(targetDir)
print(files)

# 所有的文件
fileList = [f for f in files if os.path.isfile(os.path.join(targetDir, f))]
print("-------------所有文件列表-------------")
print(fileList)

dirList = [dir for dir in files if os.path.isdir(os.path.join(targetDir, dir))]
print("-------------所有子目录列表-------------")
print(dirList)
