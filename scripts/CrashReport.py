import csv
import codecs


def readCrashFile(fpath):
    with open(fpath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # 逐行读取数据
        crashString = ""
        for row in reader:
            # 获取 event_params 列的值，并将其转换为字典
            event_params = eval(row['event_params'])
            for crashStr in event_params.values():
                crashString = crashString + crashStr + " \n"
                print(crashStr)

    save2File(crashString, "crash.text")


def save2File(dataList, fpath):
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(dataList)
    print(f"执行程序结束，文件保存在:{fpath}")


if __name__ == "__main__":
    # 打开 CSV 文件并读取数据
    fpath = '/Users/shareit/Downloads/crash_report-0301.csv'
    readCrashFile(fpath)
