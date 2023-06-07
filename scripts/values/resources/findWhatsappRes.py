import codecs
import os
import xml.etree.ElementTree as ET
import json

# whatsApp所有属性集合
whatsAppResDict = {}
"""
    主要作用：通过find_color、find_d1、find_layout、find_styles、find_yoString脚本发现的json资源，
    查找哪些资源属性是WhatsApp自带的，并保存在whatsapp.json中
"""


def findWhatsAppRes(from_dir):
    publicResDic = parserPublic(f"{from_dir}/res/values/public.xml")
    currentPath = os.getcwd()
    getResDict(f"{currentPath}/find_color/color.json", "color", publicResDic)
    getResDict(f"{currentPath}/find_layout/layout.json", "layout", publicResDic)
    getResDict(f"{currentPath}/find_styles/styles.json", "style", publicResDic)
    getResDict(f"{currentPath}/find_yoString/string_list.json", "string", publicResDic)
    save2File(whatsAppResDict, os.getcwd(), "whatsapp.json")


def parserPublic(fpath):
    parser = ET.parse(fpath)
    root = parser.getroot()
    tempDict = {}
    for child in root:
        attrib = child.attrib
        attrType = attrib.get("type")
        attrName = attrib.get("name")
        if attrType is None or attrName is None:
            continue
        if tempDict.get(attrType) is None:
            tempDict[attrType] = []
        else:
            tempDict[attrType].append(attrName)
    return tempDict


def getResDict(fpath, type, publicResDic):
    # 初始化
    if whatsAppResDict.get(type) is None:
        whatsAppResDict[type] = []
    publicDict = publicResDic.get(type)
    with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
        dataList = json.loads(rf.read())
        for item in dataList:
            # print(item)
            if item in publicDict and item not in whatsAppResDict[type]:
                whatsAppResDict[type].append(item)


def save2File(dataList, folder_path, fileName):
    os.chdir(folder_path)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,结果保存到：{os.path.join(folder_path, fileName)}")


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    findWhatsAppRes(from_dir)
