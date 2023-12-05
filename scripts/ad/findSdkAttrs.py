import codecs
import json
import os
# 所有未注册的属性集合
allAttrs = {}
# 是否允许去除文件后缀
enableRemoveFileSuffix = False

"""
    主要作用:查找正向代码sdk中xml布局属性并保存到ad/sdkAttr.json文件中。
"""


def findAllAttrs():
    if enableRemoveFileSuffix:
        readConfig("newVersionSdkPathConfig.json", "newSdkAttr.json")
    else:
        readConfig("oldVersionSdkPathConfig.json", "oldSdkAttr.json")


def readConfig(jsonFileName, saveJsonName):
    sdkPathList = readPathList(jsonFileName)
    for path in sdkPathList:
        transFolder(path)
        save2File(allAttrs, saveJsonName)


def readPathList(path):
    with codecs.open(path, encoding="utf-8", mode="r") as rf:
        return json.loads(rf.read())


def transFolder(from_dir):
    listdir = os.listdir(from_dir)
    for fName in listdir:
        fPath = os.path.join(from_dir, fName)
        if os.path.isdir(fPath) and not fName.__contains__("values"):
            fileType = fName
            if fName.__contains__("-"):
                fileType = fName.split("-")[0]
            if allAttrs.get(fileType) is None:
                allAttrs[fileType] = []
            filesList = os.listdir(fPath)
            for fileName in filesList:
                if enableRemoveFileSuffix:
                    fileName = fileName[0:fileName.index(".")]
                if fileName not in allAttrs.get(fileType):
                    allAttrs[fileType].append(fileName)


def save2File(dataList, fpath):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，文件保存在:{fpath}")


if __name__ == "__main__":
    findAllAttrs()
