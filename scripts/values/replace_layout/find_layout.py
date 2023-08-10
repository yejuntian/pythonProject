import codecs
import json
import os
import re

# 匹配到的对应关系
mappingName = {}
# 新版layout对象集合
new_layout_list = []
# 旧版layout对象集合
old_layout_list = []
# 用于存放已查找到的layout映射集合
layoutList = []
# 是否保持文件
isSaveFile = False


class LayoutEntity:
    def __init__(self, fileName, idList, ids, labelStr, numberStr, childCount, newFileName, includeLayoutList):
        self.fileName = fileName
        self.idList = idList
        self.ids = ids
        self.labelStr = labelStr
        self.numberStr = numberStr
        self.childCount = childCount
        self.newFileName = newFileName
        self.includeLayoutList = includeLayoutList


def findLayout(from_dir, to_dir):
    # 新版layout
    from_layoutDir = f"{from_dir}/res/layout"
    transFolder(from_layoutDir, new_layout_list)
    if isSaveFile:
        save2File(new_layout_list, "newVersion_layout.json")
    # 旧版layout
    to_layoutDir = f"{to_dir}/res/layout"
    transFolder(to_layoutDir, old_layout_list)
    if isSaveFile:
        save2File(old_layout_list, "oldVersion_layout.json")

    mappingLayoutEntity(new_layout_list, old_layout_list)
    save2File(mappingName, "layout.json", False)
    print(f"对应关系个数为：{len(mappingName)}")


# (self, fileName, idList, ids, labelStr, childCount, newFileName):
def mappingLayoutEntity(new_layout_list, old_layout_list):
    for newEntity in new_layout_list:
        new_fileName = newEntity.fileName
        new_ids = newEntity.ids
        new_childCount = newEntity.childCount
        new_labelStr = newEntity.labelStr
        new_numberStr = newEntity.numberStr
        matchList = []

        for oldEntity in old_layout_list:
            old_fileName = oldEntity.fileName
            old_ids = oldEntity.ids
            old_childCount = oldEntity.childCount
            old_labelStr = oldEntity.labelStr

            if new_childCount == old_childCount:
                if new_childCount <= 10:
                    if new_ids == old_ids and new_labelStr == old_labelStr:
                        matchList.append((old_fileName, oldEntity))
                else:
                    if new_ids == old_ids:
                        matchList.append((old_fileName, oldEntity))

        size = len(matchList)
        if size > 1:
            mappingEntity(newEntity, new_numberStr, matchList)
            # print(f"{new_fileName} = {matchList}")
        elif size == 1:
            if not isExitLayoutMapping(matchList[0][0]):
                mappingName[new_fileName] = matchList[0][0]
                mappingIncludeLayout(newEntity, matchList[0][1])


# 映射xml中include的layout
def mappingIncludeLayout(newEntity, oldEntity):
    newIncludeLayoutList = newEntity.includeLayoutList
    oldIncludeLayoutList = oldEntity.includeLayoutList
    if newIncludeLayoutList is None or oldIncludeLayoutList is None:
        return
    else:
        size = len(newIncludeLayoutList)
        if size > 0 and size == len(oldIncludeLayoutList):
            for index in range(0, size):
                newLayoutName = newIncludeLayoutList[index]
                oldLayoutName = oldIncludeLayoutList[index]
                mappingName[newLayoutName] = oldLayoutName
                # 存放到已查找的集合列表中
                layoutList.append(oldLayoutName)


# 匹配多个情况下，进行进一步筛选
def mappingEntity(newEntity, new_numberStr, matchList):
    mappingList = []
    new_fileName = newEntity.fileName
    for fileName, entity in matchList:
        old_numberStr = entity.numberStr
        if new_numberStr == old_numberStr:
            mappingList.append(fileName)

    if len(mappingList) == 1:
        if not isExitLayoutMapping(matchList[0][0]):
            mappingName[new_fileName] = matchList[0][0]
            mappingIncludeLayout(newEntity, matchList[0][1])
    else:
        print(f"{new_fileName} = {mappingList}")


# 是否存在layout映射
def isExitLayoutMapping(fromLayoutName):
    if fromLayoutName in layoutList:
        isExit = True
    else:
        isExit = False
        layoutList.append(fromLayoutName)
    return isExit


def transFolder(from_dir, entityList):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath):
            transFolder(fpath, entityList)
        elif os.path.isfile(fpath):
            if fname.split(".")[-1] == "xml":
                with codecs.open(fpath, "r", "utf-8") as rf:
                    matchRes(fname.split(".")[0], rf.read(), entityList)


def matchRes(fname, data, entityList):
    ids = []
    # id正则
    resIdRegex = r"android:id=\"@id/(.+?)\""
    # 标签正则
    labelRegex = r"<.+? "
    # 数字正则
    numberRegex = r"\"\d+.+?\""
    # 匹配layout正则
    layoutRegex = r"<include layout=\"@layout/(\w+)\" />"

    idStr = ""
    labelStr = ""
    numberStr = ""

    matches = re.finditer(resIdRegex, data, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        groupStr = match.group(1)
        ids.append(groupStr)
        idStr = f"{groupStr}#{idStr}"
        # print(groupStr)

    matches = re.finditer(labelRegex, data, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        groupStr = match.group()
        if groupStr.__contains__("com.gbwhatsapp"):
            groupStr = groupStr.replace("com.gbwhatsapp", "com.whatsapp")
        if groupStr.__contains__("androidy"):
            groupStr = groupStr.replace("androidy", "androidx")
        labelStr = f"{groupStr}#{labelStr}"
        # print(groupStr)

    matches = re.finditer(numberRegex, data, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        groupStr = match.group()
        numberStr = f"{groupStr}#{numberStr}"
        # print(f"{fname} = {numberStr}")

    includeLayoutList = []
    matches = re.finditer(layoutRegex, data, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        includeLayoutList.append(match.group(1))

    entity = LayoutEntity(fname, ids, idStr, labelStr, numberStr, len(ids), None, includeLayoutList)
    entityList.append(entity)


def save2File(dataList, fileName, enableConvert=True):
    if enableConvert:
        listData = []
        for entity in dataList:
            dataStr = {
                "fileName": entity.fileName,
                "idList": entity.idList,
                "ids": entity.ids,
                "labelStr": entity.labelStr,
                "includeLayoutList": entity.includeLayoutList,
                "numberStr": entity.numberStr,
                "idCount": entity.childCount
            }
            listData.append(dataStr)
        jsonStr = json.dumps(listData, ensure_ascii=False, indent=2)
    else:
        jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)

    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,结果保存到：{os.path.join(os.getcwd(), fileName)}")


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.15.81/DecodeCode/Whatsapp_v2.23.15.81"
    to_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    findLayout(from_dir, to_dir)
