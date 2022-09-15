import hashlib

# 我们要产生 MD5 哈希值，就这样写代码

# 使用 md5 算法
m = hashlib.md5()

# 要计算的源数据必须是字节串格式
# 字符串对象需要encode转化为字节串对象
m.update("张三，学费已交|13ty8ffbs2v".encode())

# 产生哈希值对应的bytes对象
resultBytes = m.digest()
# 产生哈希值的十六进制表示
resultHex = m.hexdigest()
print(resultHex)
