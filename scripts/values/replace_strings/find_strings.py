import argparse
import json
import os
import xml.etree.ElementTree as ET

# from_dir/string.xml集合
dataList = []
strList = []
# 用于存放已查找到的string name集合
stringNameList = []
# 是否保存文件
isSaveFile = False

"""
    主要作用：查找两个项目，string.xml对应的关系，
    并把查询结果保存在mappingString.json中
"""


class StringEntity:
    def __init__(self, oldName, oldPreTxt, curTxt, oldNextTxt, newName, newPreTxt, newNextTxt):
        self.oldName = oldName
        self.oldPreTxt = oldPreTxt
        self.curTxt = curTxt
        self.oldNextTxt = oldNextTxt
        self.newName = newName
        self.newPreTxt = newPreTxt
        self.newNextTxt = newNextTxt

    def __repr__(self) -> str:
        return f"name = {self.oldName} newName = {self.newName} preTxt = {self.oldPreTxt}" \
               f" curTxt = {self.curTxt} nextTxt = {self.oldNextTxt}"


def findCorrectRelation(from_dir, to_dir):
    fpath = f"{from_dir}/res/values/strings.xml"
    tpath = f"{to_dir}/res/values/strings.xml"
    getStringList(fpath)
    correctRelation(tpath)
    if isSaveFile:
        save2File(package_data(), mCurrentPath, "scripts/values/replace_strings/string.json")
    # 字典推导式
    data = {entity.newName: entity.oldName for entity in dataList}
    save2File(data, mCurrentPath, "scripts/values/replace_strings/mappingString.json")


def package_data():
    list = []
    for entity in dataList:
        if not entity.newName is None:
            newMap = {
                "content": entity.curTxt,
                "oldName": entity.oldName,
                "oldPreTxt": entity.oldPreTxt,
                "oldNextTxt": entity.oldNextTxt,
                "newName": entity.newName,
                "newPreTxt": entity.newPreTxt,
                "newNextTxt": entity.newNextTxt

            }
            list.append(newMap)
    return list


def getStringList(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    size = len(root)
    for index, child in enumerate(root):
        attrib = child.attrib
        oldName = attrib.get("name")
        curTxt = child.text
        if index == 0:
            preTxt = None
            nextTxt = root[index + 1].text
        elif index == size - 1:
            nextTxt = None
            preTxt = root[index - 1].text
        else:
            preTxt = root[index - 1].text
            nextTxt = root[index + 1].text
        strList.append(curTxt)
        dataList.append(StringEntity(oldName, preTxt, curTxt, nextTxt, None, None, None))


def correctRelation(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    size = len(root)
    for index, child in enumerate(root):
        attrib = child.attrib
        name = attrib.get("name")
        if index == 0:
            preTxt = None
            nextTxt = root[index + 1].text
        elif index == size - 1:
            nextTxt = None
            preTxt = root[index - 1].text
        else:
            preTxt = root[index - 1].text
            nextTxt = root[index + 1].text
        curTxt = child.text
        count = strList.count(curTxt)
        if count == 0:
            continue
        elif count == 1:
            pos = strList.index(curTxt)
            entity = dataList[pos]
            if (preTxt == entity.oldPreTxt or nextTxt == entity.oldNextTxt) \
                    and curTxt == entity.curTxt and not isExitStr(entity.oldName):
                entity.newName = name
                entity.newPreTxt = preTxt
                entity.newNextTxt = nextTxt
                continue
        elif count > 1:
            pos = strList.index(curTxt)
            entity = dataList[pos]
            if preTxt == entity.oldPreTxt and nextTxt == entity.oldNextTxt \
                    and curTxt == entity.curTxt and not isExitStr(entity.oldName):
                entity.newName = name
                entity.newPreTxt = preTxt
                entity.newNextTxt = nextTxt
                continue
            else:
                for pos in range(pos, len(dataList)):
                    entity = dataList[pos]
                    if preTxt == entity.oldPreTxt and nextTxt == entity.oldNextTxt \
                            and curTxt == entity.curTxt and not isExitStr(entity.oldName):
                        entity.newName = name
                        entity.newPreTxt = preTxt
                        entity.newNextTxt = nextTxt
                        break


def isExitStr(str):
    if str in stringNameList:
        isExit = True
    else:
        isExit = False
        stringNameList.append(str)
    return isExit


def save2File(dataList, folder_path, fileName):
    os.chdir(folder_path)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,结果保存到：{os.path.join(folder_path, fileName)}")


if __name__ == "__main__":
    mCurrentPath = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    to_dir = args.to_dir
    # from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    # to_dir = "/Users/shareit/work/GBWorke/whatsapp_new/Whatsapp_v2.22.24.78"
    findCorrectRelation(from_dir, to_dir)
