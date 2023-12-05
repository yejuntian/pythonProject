import codecs
import json
import os

"""
    主要作用：读取ad/oldSdkAttr.json 要删除的数据列表，遍历from_dir目标进行匹配，匹配成功后进行删除。
"""


def delSdkRes(from_dir):
    allAttrs = getDelAttrs("oldSdkAttr.json")
    startDelFiles(from_dir, allAttrs)
    print(f"执行程序结束")


def getDelAttrs(fpath):
    with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
        return json.loads(rf.read())


def startDelFiles(from_dir, allAttrs):
    listdir = os.listdir(from_dir)
    for fName in listdir:
        fPath = os.path.join(from_dir, fName)
        if os.path.isdir(fPath) and not fName.__contains__("values"):
            fileType = fName
            if fName.__contains__("-"):
                fileType = fName.split("-")[0]
            filesList = os.listdir(fPath)
            delFileList = allAttrs.get(fileType)
            if delFileList is not None:
                for fileName in filesList:
                    if fileName in delFileList:
                        os.remove(os.path.join(fPath, fileName))


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.20.76/DecodeCode/Whatsapp_v2.23.20.76"
    delSdkRes(f"{from_dir}/res")
