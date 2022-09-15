import os
import time

# 返回文件或目录的大小  ====》文件大小 size = 282
os_path_getsize = os.path.getsize("../15-文件和目录/1-创建目录.py")
print(f"文件大小 size = {os_path_getsize}")

# 返回文件或目录的大小  ====》目录大小 size = 352
os_path_getsize = os.path.getsize("../15-文件和目录/")
print(f"目录大小 size = {os_path_getsize}")

# 返回文件的最后修改日期，时间单位为秒
path_getmtime = os.path.getmtime("../15-文件和目录/")
print(f"修改目录时间为 time = {path_getmtime}")

# 可以把秒时间 转化为日期时间
ctime = time.ctime(os.path.getctime("../15-文件和目录/1-创建目录.py"))
print(f"秒转为日期时间为：time = {ctime}")
