import glob

# 得到目录中指定扩展名的文件和子目录
# 可以使用glob库

# 在含有"文件"的目录下查找后缀为.py格式的文件
glob_glob = glob.glob(r"../../pythonProject/*文件*/*.py")
print(len(glob_glob))
