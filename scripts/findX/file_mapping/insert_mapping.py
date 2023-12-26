import argparse
import codecs
import json
import os

# base版本号
baseVersion = "2.23.20.76"
# 插入版本号
insertVersion = "2.23.25.76"
# 是否插入plus
isInsertPlus = False

"""
    基于baseVersion版本号，查找insertVersion对应的关系，
    并插入到指定位置。
    from_path:要插入的json文件绝对路径
"""


def replace_X(tpath):
    if not isInsertPlus:
        curPath = os.path.join(os.getcwd(), "scripts/findX/file_mapping/classMapping.json")
    else:
        curPath = os.path.join(os.getcwd(), "scripts/findX/class.json")
    # print(curPath)
    newJson = getJsonData(tpath)
    oldJson = getJsonData(curPath)
    for newItem in newJson:
        # 是否包含->
        isContains = False
        new_item_value = newItem[baseVersion]
        if new_item_value.__contains__("->"):
            isContains = True
            new_item_value = new_item_value.split("->")[0]
        isFind = False
        for oldItem in oldJson:
            old_item_value = oldItem[baseVersion]
            if old_item_value == new_item_value:
                isFind = True
                if isContains:
                    newItem[insertVersion] = f"{oldItem[insertVersion]}->"
                else:
                    newItem[insertVersion] = oldItem[insertVersion]
        if not isFind:
            if isContains:
                newItem[insertVersion] = "->"
            else:
                newItem[insertVersion] = ""
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

    # from_path = "/Users/shareit/work/pythonProject/scripts/findX/class.json"
    from_path = args.from_dir
    replace_X(from_path)
