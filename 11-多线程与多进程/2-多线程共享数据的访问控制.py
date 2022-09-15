from threading import *
from time import *

# 多个线程里面的代码 需要访问 同一个 公共的数据对象
bank = {
    'byhy': 0
}
# 创建锁对象
bankLock = Lock()
# 定义一个函数，作为新线程执行的入口函数
def deposit(threadId, amount):
    # 申请锁
    bankLock.acquire()
    balance = bank["byhy"]
    # 执行一些任务，耗费了0.1秒
    sleep(0.1)
    bank["byhy"] = balance + amount
    print(f"子线程{threadId}执行结束")
    # 申请锁
    bankLock.release()


theadList = []

for threadId in range(10):
    thread = Thread(target=deposit,
                    args=(threadId, 1))
    thread.start()
    # 把线程对象都存储到threadList中
    theadList.append(thread)

for thread in theadList:
    thread.join()

print('主线程结束')
print(f'最后我们的账号余额为 {bank["byhy"]}')
