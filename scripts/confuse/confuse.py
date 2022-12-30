import os
import xml.etree.ElementTree as ET
import json
import codecs

filePath = "public.xml"
blackTypeStr = ["bool", "drawable", "id", "raw"]
mappingStr = {}
# GB使用的映射列表
gbMapping = {}
# 文件类型映射关系列表
filelist = {"color": "json_data/color.json",
            "style": "json_data/style.json",
            "layout": "json_data/layout.json",
            "string": "json_data/string.json"}
# WhatsApp不需要混淆的属性集合
originMapping = {}
# 是否要保存测试文件
enableSaveFile = False


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
        save2File(originMapping, "whatsapp.json")


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
                    mappingStr[name] = f"{newName}#{type}"
                else:
                    print(f'<public type="{type}" name="{name}" id="{id}" />')

    save2File(mappingStr, "mapping.json")


def save2File(dataList, fileName):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fileName, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，文件保存在:{os.path.join(os.getcwd(), fileName)}")


def getNewName(type, id):
    newId = id[5:]
    return f"{type}{newId}"


if __name__ == "__main__":
    for key, value in filelist.items():
        loadData(key, value)
    findNotConfuseAttr(filePath, gbMapping)
    addMapping(filePath)
