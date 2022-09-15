import shutil

# shutil 模块里面有很多 目录文件操作的函数
# 拷贝文件，可以使用shutil模块的copyfile函数。


# 如果拷贝前，1-创建目录_copy.py 已经存在，则会被拷贝覆盖
shutil.copyfile("1-创建目录.py","1-创建目录_copy.py")