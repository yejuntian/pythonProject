import codecs
import json
import os
import xml.etree.ElementTree as ET
import argparse

mappingStr = {}
# GB使用的映射列表
gbMapping = {}
# 文件类型映射关系列表
curPath = f"{os.getcwd()}/scripts/values/native_values"
filelist = {"color": f"{curPath}/json_data/colors.json",
            "style": f"{curPath}/json_data/styles.json",
            "layout": f"{curPath}/json_data/layouts.json",
            "string": f"{curPath}/json_data/strings.json"}
# WhatsApp不需要混淆的属性集合
originMapping = {}

"""
    主要作用：读取json_data目录下的json,
    获取GBWhatsApp需要的values属性并保存到whatsapp.json，
    查找strings.xml的对应关系保存到FindString.json；
    未发现的values属性保存到GBNeedToFind.json
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
def findNativeValues(fpath, mappingData):
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

    save2File(originMapping, "whatsapp.json")


# 查找GB需要的属性,通过脚本没有查找到的属性映射
def findNotFoundAttr(from_dir, to_dir, originMapping):
    fpath = f"{to_dir}/res/values/public.xml"
    parser = ET.parse(fpath)
    root = parser.getroot()
    # GB所需要的属性，但是通过映射关系没有查找的属性name
    gb_dict = {}
    for child in root:
        attrib = child.attrib
        type = attrib.get("type")
        name = attrib.get("name")
        id = attrib.get("id")
        if id is None or type is None or name is None:
            continue

        if gb_dict.get(type) is None:
            gb_dict[type] = []
        gb_dict[type].append(name)

    # 遍历查询没有映射的属性name
    temp_dict = {}
    for attrType, nameList in originMapping.items():
        dataList = gb_dict.get(attrType)
        if not dataList is None and len(dataList) > 0:
            for attrName in nameList:
                if not attrName in dataList:
                    if temp_dict.get(attrType) is None:
                        temp_dict[attrType] = []
                    temp_dict[attrType].append(attrName)

    findStringMapping(from_dir, to_dir, temp_dict.get("string"), temp_dict)


# 根据stringList列表，查找values/strings.xml对应关系
def findStringMapping(from_dir, to_dir, stringList, dict_list):
    if stringList is None or len(stringList) <= 0: return
    oldStringDict = getStringList(f"{from_dir}/res/values/strings.xml")
    newStringDict = getStringList(f"{to_dir}/res/values/strings.xml")
    stringDict = {}
    for name in stringList:
        stringDict[name] = oldStringDict.get(name)

    stringMappingList = []
    dataList = []
    # 防止name重复映射同一个
    tempList = []
    for oldAttrName, oldAttrText in stringDict.items():
        isFind = False
        for attrName, attrText in newStringDict.items():
            if attrName.startswith("APKTOOL_DUMMYVAL") and not attrName in tempList and attrText == oldAttrText:
                isFind = True
                tempList.append(attrName)
                stringMappingList.append({"oldName": oldAttrName, "newName": attrName})
                break
        if not isFind:
            dataList.append(oldAttrName)
    dict_list["string"] = dataList
    save2File(stringMappingList, "FindString.json")
    save2File(dict_list, "GBNeedToFind.json")


# 获取values/strings.xml属性name和文本text的映射关系
def getStringList(fpath):
    stringDict = {}
    parser = ET.parse(fpath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        text = child.text
        name = attrib.get("name")
        if not name is None:
            stringDict[name] = text
    return stringDict


def save2File(dataList, fileName):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fileName, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，文件保存在:{os.path.join(os.getcwd(), fileName)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    args = parser.parse_args()

    from_dir = args.from_dir
    to_dir = args.to_dir
    # from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    # to_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.22.24.78"

    for key, value in filelist.items():
        loadData(key, value)

    filePath = f"{from_dir}/res/values/public.xml"
    # 找着whatsapp不需要混淆的属性
    findNativeValues(filePath, gbMapping)
    # 查找GB需要的属性,通过脚本没有查找到的属性映射
    findNotFoundAttr(from_dir, to_dir, originMapping)
