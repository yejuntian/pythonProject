import os
import xml.etree.ElementTree as ET
import json
import argparse
import codecs

blackTypeStr = ["bool", "drawable", "font", "mipmap", "id", "raw"]
# 存放public.xml映射关系
mappingStr = {}
# GB使用的映射列表
gbMapping = {}
# 文件类型映射关系列表
filelist = {"color": "scripts/confuse/json_data/color.json",
            "style": "scripts/confuse/json_data/style.json",
            "layout": "scripts/confuse/json_data/layout.json",
            "string": "scripts/confuse/json_data/string.json"}
# WhatsApp不需要混淆的属性集合
originMapping = {}
# 是否要保存测试文件
enableSaveFile = True

"""
    主要作用：根据json_data目录下的映射关系列表，对比public.xml文件，
    输出需要混淆的属性，最终保存到confuse/mapping.json文件中。
"""


# 加载gb所有的属性name
def loadData(type, fpath):
    if gbMapping.get(type) is None:
        gbMapping[type] = []

    with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
        data = json.loads(rf.read())
        for item in data:
            if not str(item) in gbMapping.get(type):
                gbMapping[type].append(item)


# 找着不需要混淆的属性
def findNotConfuseAttr(fpath, mappingData):
    parser = ET.parse(fpath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        type = attrib.get("type")
        name = attrib.get("name")
        id = attrib.get("id")
        if id is None or type is None or name is None:
            continue
        dataList = mappingData.get(type)
        if not dataList is None and len(dataList) > 0:
            if name in dataList:
                if originMapping.get(type) is None:
                    originMapping[type] = []
                originMapping[type].append(name)
    if enableSaveFile:
        save2File(originMapping, f"{mCurrentPath}/scripts/confuse/whatsapp.json")


def addMapping(fpath):
    parser = ET.parse(fpath)
    root = parser.getroot()

    for child in root:
        attrib = child.attrib
        type = attrib.get("type")
        name = attrib.get("name")
        id = attrib.get("id")
        if id is None or type is None or name is None:
            continue
        if not type in blackTypeStr:
            dataList = originMapping.get(type)
            if not dataList is None and name in dataList:
                continue
            else:
                newName = getNewName(type, id)
                if mappingStr.get(name) is None:
                    mappingStr[f"{name}#{type}"] = f"{newName}#{type}"
                else:
                    print(f'<public type="{type}" name="{name}" id="{id}" />')

    save2File(mappingStr, f"{mCurrentPath}/scripts/confuse/mapping.json")


def save2File(dataList, fpath):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，文件保存在:{fpath}")


def getNewName(type, id):
    newId = id[6:]
    return f"{type}{newId}"


if __name__ == "__main__":
    mCurrentPath = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    filePath = f"{from_dir}/res/values/public.xml"
    for key, value in filelist.items():
        loadData(key, value)
    findNotConfuseAttr(filePath, gbMapping)
    addMapping(filePath)
