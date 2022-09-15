import os

# 会在当前工作目录下面创建 tmp目录，在tmp目录下面再创建 python目录，在Python目录下面再创建fileop目录
# exist_ok=True 指定了，如果某个要创建的目录已经存在，也不报错
os.makedirs("tmp/python/fileop", exist_ok=True)
