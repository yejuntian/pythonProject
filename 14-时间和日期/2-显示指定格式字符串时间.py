from datetime import datetime
import time
import dateutil.parser

# 得到类似这样的字符串 2022-08-10 19:24:08.719453
print(str(datetime.now()))

# 得到类似这样的字符串： 2022-08-10 ** 19-26-25
formatTime = datetime.now().strftime("%Y-%m-%d ** %H-%M-%S")
print("formatTime = " + formatTime)

# 使用time库来格式化显示字符串 2022-08-10 ** 19-43-53
formatTime = time.strftime("%Y-%m-%d ** %H-%M-%S", time.localtime())
print("formatTime = " + formatTime)

# 数字表示的时间转化为字符串表示 （2015年06月17日 08时:55分:29秒）
time1 = time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(1434502529))
print("time = " + time1)

# 将字符串指定的时间，转化为秒数时间 mktime = 1438444799
strptime = time.strptime("2015-08-01 23:59:59", "%Y-%m-%d %H:%M:%S")
print(strptime)
mktime = int(time.mktime(strptime))
print("mktime = " + str(mktime))

# ISO格式 转化为 本地时间
# 字符串时间 转化为 datetime 对象
datme = dateutil.parser.isoparse("2008-09-03T20:56:35.450686+00:00")
# 转化为本地时区的 datetime 对象
astimezone = datme.astimezone(tz=None)
# 产生本地格式 字符串 2008-09-04 04:56:35
strftime = astimezone.strftime("%Y-%m-%d %H:%M:%S")
print(strftime)
