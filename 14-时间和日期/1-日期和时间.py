import time


def func1():
    time.sleep(1)
    print("执行func1函数")


# time.time() 会返回 从 1970年1月1日0点到 当前时间的 经过的秒数
before = time.time()
func1()
after = time.time()

print(f"调用func1()函数花费时间为：{after - before}")

# 使用time库来格式化显示字符串
currentTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("currentTime = " + currentTime)

# 数字表示的时间转化为字符串表示 （2015年06月17日 08时:55分:29秒）
time = time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(1434502529))
print("time = " + time)

