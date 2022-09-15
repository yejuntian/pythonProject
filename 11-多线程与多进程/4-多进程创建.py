from multiprocessing import Process


def f():
    while True:
        b = 53 * 53


if __name__ == '__main__':
    plist = []
    for i in range(2):
        p = Process(target=f)
        p.start()
        plist.append(p)

    for p in plist:
        p.join()
