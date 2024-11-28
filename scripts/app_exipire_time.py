import time

"""
 主要作用：用于计算whatsApp过期时间
"""

# whatsapp 构建时间
baseTime = 1731954976000 / 1000
day = 270
# whatsapp 内置过期时间
waExpireDay = 90
print(f'1、WhatsApp基础版本更新时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(baseTime))}')

print(f'2、WhatsApp升级时间计算逻辑是否更新:否')

currentTime = baseTime + (day - 6) * 86400
print(f'3、WhatsApp到期时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(currentTime))}')

currentTime = baseTime + ((day - 6) - 30) * 86400
print(f'4、WhatsApp促升级开始时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(currentTime))}')

currentTime = baseTime + ((day - 6) + 15) * 86400
print(f'5、WhatsApp登录强升级开始时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(currentTime))}')

currentTime = baseTime + (waExpireDay - 6) * 86400
print(f'6、WhatsApp原始的过期最早时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(currentTime))}')

currentTime = baseTime + (waExpireDay + 7) * 86400
print(f'7、WhatsApp原始的过期最晚时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(currentTime))}')

currentTime = baseTime + day * 86400
print(f'8、GB版本内置{day}天升级时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(currentTime))}')

print(f'9、GB版本内置{day}天升级时间对应毫秒：{str(float(currentTime * 1000)).split(".")[0]}')
