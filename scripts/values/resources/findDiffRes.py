import codecs
import json
import os

# diffRes所有属性集合
diffResDict = {}
"""
    主要作用：加载json文件，对比whatsapp.json找出whatsapp.json中不存在的属性保存到diff.json中
"""


def findDiffRes(fpath, type):
    jsonDict = getJsonData(f"{os.getcwd()}/whatsapp.json")
    jsonList = getJsonData(fpath)
    listData = jsonDict[type]

    if diffResDict.get(type) is None:
        diffResDict[type] = []
    for item in jsonList:
        if item not in listData:
            diffResDict[type].append(item)
    save2File(diffResDict, os.getcwd(), "diff.json")


def save2File(dataList, folder_path, fileName):
    os.chdir(folder_path)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,结果保存到：{os.path.join(folder_path, fileName)}")


def getJsonData(fpath):
    with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
        return json.loads(rf.read())


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/pythonProject/scripts/values/native_values/json_data/styles.json"
    findDiffRes(from_dir, "style")
