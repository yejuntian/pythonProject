import json
import os
import xml.etree.ElementTree as ET

# from_dir/colors.xml集合
from_dataList = []
# to_dir/colors.xml集合
to_dataList = []
# from_dir/colors.xml所有颜色的16进制色值集合
allFromColors = []
colorList = []
repeatStrList = []

"""
    主要作用：查找两个项目，colors.xml对应的关系，
    并把查询结果保存在colors.json中
"""


class StringEntity:
    def __init__(self, colorName, curColor, preColor, nextColor):
        self.colorName = colorName
        self.curColor = curColor
        self.preColor = preColor
        self.nextColor = nextColor

    def __repr__(self) -> str:
        return f"colorName = {self.colorName} preColor = {self.preColor}" \
               f" curColor = {self.curColor} nextColor = {self.nextColor}"


def findCorrectRelation(from_dir, to_dir):
    fpath = f"{from_dir}/res/values/colors.xml"
    tpath = f"{to_dir}/res/values/colors.xml"
    setColorList(fpath, True)
    setColorList(tpath, False)
    # save2File(package_data(from_dataList), os.getcwd(), "colors_old.json")
    # save2File(package_data(to_dataList), os.getcwd(), "colors_new.json")
    correctRelation()
    # save2File(package_data(), os.getcwd(), "colors.json")


def package_data(dataList):
    list = []
    for entity in dataList:
        newMap = {
            "colorName": entity.colorName,
            "curColor": entity.curColor,
            "preColor": entity.preColor,
            "nextColor": entity.nextColor
        }
        list.append(newMap)
    return list


def setColorList(fpath, isFromPath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    size = len(root)
    colorMapping = {}
    for index, child in enumerate(root):
        attrib = child.attrib
        colorName = attrib.get("name")
        curColor = child.text
        if index == 0:
            preColor = None
            nextColor = root[index + 1].text
        elif index == size - 1:
            nextColor = None
            preColor = root[index - 1].text
        else:
            preColor = root[index - 1].text
            nextColor = root[index + 1].text
        colorMapping[colorName] = curColor
        if isFromPath:
            from_dataList.append(StringEntity(colorName, curColor, preColor, nextColor))
        else:
            to_dataList.append(StringEntity(colorName, curColor, preColor, nextColor))
    addColorMapping(fpath, colorMapping, isFromPath)


# 添加color映射
def addColorMapping(fpath, colorMapping, isFromPath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    size = len(root)
    for index, child in enumerate(root):
        curColor = child.text.strip()
        if index == 0:
            preColor = None
            nextColor = getColor(root[index + 1].text, colorMapping)
        elif index == size - 1:
            nextColor = None
            preColor = getColor(root[index - 1].text, colorMapping)
        else:
            preColor = getColor(root[index - 1].text, colorMapping)
            nextColor = getColor(root[index + 1].text, colorMapping)

        if isFromPath:
            if curColor.startswith("@color/"):
                mColor = getColor(curColor, colorMapping)
                if mColor.__contains__("$"):
                    mColor = mColor.split("$")[1]
                allFromColors.append(mColor)
            else:
                allFromColors.append(curColor)
            packageEntityData(from_dataList, index, curColor, preColor, nextColor, colorMapping)
        else:
            packageEntityData(to_dataList, index, curColor, preColor, nextColor, colorMapping)


# 组装数据
def packageEntityData(dataList, index, curColor, preColor, nextColor, colorMapping):
    entity = dataList[index]
    if curColor.startswith("@color/"):
        entity.curColor = getColor(curColor, colorMapping)
    entity.preColor = preColor
    entity.nextColor = nextColor


# 获取16进制颜色值
def getColor(colorTxt, colorMapping):
    if colorTxt.startswith("@color/"):
        colorName = colorTxt.split("/")[1]
        colorValue = colorMapping.get(colorName)
        while colorValue.startswith("@color/"):
            colorName = colorValue.split("/")[1]
            colorValue = colorMapping.get(colorName)
        return f"{colorTxt}${colorValue}"
    return colorTxt


def correctRelation():
    print(f"colorsSize = {len(allFromColors)} size = {len(from_dataList)}")
    print(allFromColors)
    size = len(to_dataList)
    for index, toEntity in enumerate(to_dataList):
        curColor = getCorrectColor(toEntity.curColor)
        if index == 0:
            preColor = None
            nextColor = getCorrectColor(to_dataList[index + 1].curColor)
        elif index == size - 1:
            preColor = getCorrectColor(to_dataList[index - 1].curColor)
            nextColor = None
        else:
            preColor = getCorrectColor(to_dataList[index - 1].curColor)
            nextColor = getCorrectColor(to_dataList[index + 1].curColor)

        # print(f"name = {toEntity.colorName} curColor = {curColor} preColor = {preColor} nextColor = {nextColor}")


def getCorrectColor(colorTxt):
    if colorTxt.__contains__("$"):
        return colorTxt.split("$")[1]
    return colorTxt


# def correctRelation(fpath):
#     parse = ET.parse(fpath)
#     root = parse.getroot()
#     size = len(root)
#     for index, child in enumerate(root):
#         attrib = child.attrib
#         name = attrib.get("name")
#         if index == 0:
#             preColor = None
#             nextColor = root[index + 1].text
#         elif index == size - 1:
#             nextColor = None
#             preColor = root[index - 1].text
#         else:
#             preColor = root[index - 1].text
#             nextColor = root[index + 1].text
#         oldPreColor = child.text
#         count = colorList.count(oldPreColor)
#         if count == 0:
#             continue
#         elif count == 1:
#             pos = colorList.index(oldPreColor)
#             entity = dataList[pos]
#             if preColor == entity.oldPreColor or nextColor == entity.oldNextColor:
#                 entity.newColorName = name
#                 entity.newPreColor = preColor
#                 entity.newNextColor = nextColor
#                 repeatStrList.append(f"{name}#{entity.oldPreColorName}")
#                 continue
#         elif count > 1:
#             pos = colorList.index(oldPreColor)
#             entity = dataList[pos]
#             if preColor == entity.oldPreColor and nextColor == entity.oldNextColor:
#                 entity.newColorName = name
#                 entity.newPreColor = preColor
#                 entity.newNextColor = nextColor
#                 continue
#             else:
#                 for pos in range(pos, len(dataList)):
#                     entity = dataList[pos]
#                     if preColor == entity.oldPreColor and nextColor == entity.oldNextColor:
#                         entity.newColorName = name
#                         entity.newPreColor = preColor
#                         entity.newNextColor = nextColor
#                         break


def save2File(dataList, folder_path, fileName):
    os.chdir(folder_path)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,结果保存到：{os.path.join(folder_path, fileName)}")


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("from_dir")
    # parser.add_argument("to_dir")
    # args = parser.parse_args()

    # from_dir = args.from_dir
    # to_dir = args.from_dir
    from_dir = "/Users/shareit/work/GBWorke/wagb/DecodeCode/WhatsApp_v2.22.18.70"
    to_dir = "/Users/shareit/work/GBWorke/whatsapp_new/whatsapp_v2.22.25.11"
    findCorrectRelation(from_dir, to_dir)