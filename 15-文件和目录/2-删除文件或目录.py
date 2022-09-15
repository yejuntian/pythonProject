import os
import shutil

# os.remove 可以删除一个文件，比如
# os.remove('__init__.py')

# shutil.rmtree() 可以递归的删除某个目录所有的子目录和子文件
# ignore_errors=True 保证如果目录不为空，不会抛出异常
shutil.rmtree("tmp", ignore_errors=True)
