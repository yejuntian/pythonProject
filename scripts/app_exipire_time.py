import time

"""
 主要作用：用于计算whatsApp过期时间
"""

# whatsapp 构建时间
baseTime = 1666631460000 / 1000
print(f'1、WhatsApp基础版本更新时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(baseTime))}')

print(f'2、WhatsApp升级时间计算逻辑是否更新:否')

currentTime = baseTime + (180 - 6) * 86400
print(f'3、WhatsApp到期时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(currentTime))}')

currentTime = baseTime + ((180 - 6) - 30) * 86400
print(f'4、WhatsApp促升级开始时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(currentTime))}')

currentTime = baseTime + ((180 - 6) + 15) * 86400
print(f'5、WhatsApp登录强升级开始时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(currentTime))}')

currentTime = baseTime + (180 + 7) * 86400
print(f'6、GB版本内置本地升级时间:{time.strftime("%Y年%m月%d日 %H时:%M分:%S秒", time.localtime(currentTime))}')

print(f'7、GB版本内置本地升级时间对应毫秒：{str(float(currentTime * 1000)).split(".")[0]}')
