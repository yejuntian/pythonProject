import argparse
import codecs
import json
import os

fileList = ['class2.json', 'field2.json', 'method2.json']
baseVersion = "2.22.18.70"
insertVersion = "2.22.10.73"

"""
    基于baseVersion版本号，查找insertVersion对应的关系，
    并插入到指定位置。
"""


def replace_X(from_dir):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath):
            replace_X(fpath)
        elif os.path.isfile(fpath):
            if fname in fileList:
                startReplace(fpath, fname)


def getJsonData(fpath):
    with codecs.open(fpath, "r", "utf-8") as rfile:
        return json.loads(rfile.read())


def startReplace(fpath, fname):
    curPath = os.path.join(os.getcwd(), f"scripts/findX/{fname}")
    oldJson = getJsonData(fpath)
    newJson = getJsonData(curPath)
    for newItem in newJson:
        new_item_value = newItem[baseVersion]
        for oldItem in oldJson:
            old_item_value = oldItem[baseVersion]
            if old_item_value == new_item_value:
                newItem[insertVersion] = oldItem[insertVersion]
    save2File(curPath, newJson)


def save2File(fpath, dataList):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fpath, "w+") as wf:
        wf.write(jsonStr)
    print(f"程序执行结束，结果保存在{fpath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    replace_X(args.from_dir)
