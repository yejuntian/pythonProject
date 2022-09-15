import os

# 修改目录名 testCopy 为 test1Copy
# os.rename('../testCopy','../test1Copy')

# 修改文件名 test1Copy/copy/Test1.py 为 test1Copy/copy/Test2.py
os.rename('../test1Copy/copy/Test1.py', '../test1Copy/copy/Test2.py')
