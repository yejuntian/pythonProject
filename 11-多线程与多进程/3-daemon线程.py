from threading import Thread
from time import sleep


# 设置daemon参数值为True ，要等到设置daemon=true的程序结束，程序才会结束
# 再次运行，可以发现，只要主线程结束了，整个程序就结束了。因为只有主线程是非daemon线程
def threadFunc():
    sleep(2)
    print('子线程 结束')


thread = Thread(target=threadFunc,
                # 设置新线程
                daemon=True
                )
thread.start()
print('主线程结束')

