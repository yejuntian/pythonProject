import codecs
import json
import os
import shutil

typeList = ["animator", "color", "drawable", "layout", "anim"]
# 只匹配下面的文件类型
extends = ["png", "xml", "jpg"]
dataPath = f"../values/native_values/GBNeedToFind.json"

"""
 主要作用：根据dataPath指定的路径加载json数据，
 从from_dir复制typeList类型的xml/png等资源文件，
 copy到to_dir目标项目中
"""


def copyResource(from_dir, to_dir):
    mappingData = loadData(dataPath)
    # print(mappingData)
    transFolderCopy(f"{from_dir}/res", f"{to_dir}/res", mappingData)


def transFolderCopy(from_dir, to_dir, mappingData):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        tpath = os.path.join(to_dir, fname)
        if os.path.isdir(fpath):
            transFolderCopy(fpath, tpath, mappingData)
        elif os.path.isfile(fpath):
            if fname.split(".")[-1] in extends:
                fileName = fname.split(".")[0]
                folderName = fpath.split("/")[-2]
                # 目标文件夹列表
                parentFolderPath = os.path.dirname(tpath)
                if not os.path.exists(parentFolderPath):
                    os.makedirs(parentFolderPath, exist_ok=True)
                folderList = os.listdir(parentFolderPath)
                if folderName.__contains__("-"):
                    folderName = folderName.split("-")[0]
                if folderName == "mipmap" or folderName == "drawable":
                    drawableList = mappingData.get("drawable")
                    # 在copy列表中，并且目标文件夹不存在则进行copy操作
                    if fileName in drawableList and not fname in folderList:
                        shutil.copy(fpath, tpath)
                elif folderName in typeList:
                    otherFileList = mappingData.get(folderName)
                    # 在copy列表中，并且目标文件夹不存在则进行copy操作
                    if fileName in otherFileList and not fname in folderList:
                        shutil.copy(fpath, tpath)


def loadData(fpath):
    newDict = {}
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = json.loads(rf.read())
        for type, nameList in data.items():
            if type in typeList:
                if newDict.get(type) is None:
                    newDict[type] = []
                for name in nameList:
                    if not name in newDict[type]:
                        newDict[type].append(name)
    return newDict


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    to_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.23.2.76"
    copyResource(from_dir, to_dir)
