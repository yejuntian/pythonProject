import time


def getXXXTime():
    return time.strftime('%Y_%m_%d %H:%M:%S', time.localtime())


# 不去修改原来的函数 ， 而是 使用装饰器
# 定义一个装饰器函数  （注意：函数里面可以再次定义函数）
def sayLocal(fun):
    def wrapper():
        curTime = fun()
        return f"当地时间：{curTime}"

    return wrapper


# 装饰 getXXXTime
getXXXTime = sayLocal(getXXXTime)
print("第一种方式" + getXXXTime())


# 第二种方式


def sayLocal2(fun):
    def wrapper():
        curTime = fun()
        return f"当地时间：{curTime}"

    return wrapper


@sayLocal2
def getXXXTime2():
    return time.strftime('%Y_%m_%d %H:%M:%S', time.localtime())


print("第二种方式" + getXXXTime2())
