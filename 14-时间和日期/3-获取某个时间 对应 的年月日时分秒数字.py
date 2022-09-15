from datetime import datetime, timedelta
from calendar import monthrange

now = datetime.now()

# 年
print(now.year)

# 月
print(now.month)

# 日
print(now.day)

# 时
print(now.hour)

# 分
print(now.minute)

# 秒
print(now.second)

# 毫秒
print(now.microsecond)

# 获取星期几用 weekday()方法
# 0 代表星期一，1 代表星期二 依次类推

print(now.weekday())

# 1-获得指定时间字符串对应星期几
thatDay = "2018-6-24"

strptime = datetime.strptime(thatDay, "%Y-%m-%d")

print(strptime.weekday())

# 2-从某个时间点往前或者后推 一段时间

thatDay = "2018-6-24"
theDay = datetime.strptime(thatDay, "%Y-%m-%d").date()
# 后推120天 就是theDay + timedelta(days=120)   -->2018-10-22
targetData = theDay + timedelta(days=120)
print(targetData)
print(targetData.weekday())

# 前推120天 就是theDay - timedelta(days=120) --->2018-02-24
target = theDay - timedelta(days=120)

print(target)
print(target.weekday())

# 3-获取某个月总共有多少天


# monthrange返回的是元组
# 第一个元素是指定月第一天是星期几
# 第二个元素是指定月有多少天

mr = monthrange(2022, 8)
print(f"8月第一天是星期：{mr[0]} 8月份一共{mr[1]}天")
