import argparse
import codecs
import json
import os

baseVersion = "2.22.22.80"
insertVersion = "2.23.2.76"

"""
    基于baseVersion版本号，查找insertVersion对应的关系，
    并插入到指定位置。
"""


def replace_X(tpath):
    curPath = os.path.join(os.getcwd(), "scripts/findX/file_mapping/classMapping.json")
    newJson = getJsonData(tpath)
    oldJson = getJsonData(curPath)
    for newItem in newJson:
        new_item_value = newItem[baseVersion]
        for oldItem in oldJson:
            old_item_value = oldItem[baseVersion]
            if old_item_value == new_item_value:
                newItem[insertVersion] = oldItem[insertVersion]
    save2File(tpath, newJson)


def getJsonData(fpath):
    with codecs.open(fpath, "r", "utf-8") as rfile:
        return json.loads(rfile.read())


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
