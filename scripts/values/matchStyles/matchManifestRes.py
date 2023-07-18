import os
import json
import re
import xml.etree.ElementTree as ET
import argparse

# android命名空间约束
android_scheme = "http://schemas.android.com/apk/res/android"
regex = r"(\'|\")@(.*?)/(.*?)(\'|\")"
from_dict = {}
to_dict = {}
# 保存对应关系集合
mapDict = {}
mCurrentPath = ""

"""
    主要作用：匹配androidManifest.xml中混淆属性的对应关系，并保存到scripts/values/replace_layout/layout.json
"""


def findResMapping(from_path, to_path):
    parserXml(to_path, to_dict)
    parserXml(from_path, from_dict)
    mappingRelation()
    save2File(mapDict, f"{mCurrentPath}/scripts/values/replace_layout/layout.json")


def save2File(dataList, fileName):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,结果保存到：{os.path.join(os.getcwd(), fileName)}")


# 映射对应关系
def mappingRelation():
    for attrName, attrList in from_dict.items():
        to_AttrList = to_dict.get(attrName)
        if to_AttrList is not None and (len(to_AttrList) == len(attrList)):
            for i in range(len(attrList)):
                keys1 = set(attrList[i].keys())
                keys2 = set(to_AttrList[i].keys())
                # 比较key值都相同的情况下，依次取出每个字典对应的value值
                if keys1 == keys2:
                    fromAttrValue = list(attrList[i].values())
                    toAttrValue = list(to_AttrList[i].values())
                    # zip()函数将两个列表打包在一起
                    for value1, value2 in zip(fromAttrValue, toAttrValue):
                        if value1.startswith("APKTOOL_DUMMYVAL_"):
                            mapDict[value1] = value2


def parserXml(fpath, dict):
    ET.register_namespace('android', android_scheme)
    nameSpace = "{" + android_scheme + "}"
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        tag = child.tag
        if tag == "queries":
            pass
        elif tag == "application":
            tempList = getAttrList(str(attrib))
            dict["application"] = tempList
            for subChild in child:
                suAttrib = subChild.attrib
                subName = suAttrib.get(f"{nameSpace}name")
                subChildStr = ET.tostring(subChild, encoding="utf-8").decode('utf-8')
                tempList = getAttrList(subChildStr)
                if len(tempList) > 0:
                    dict[subName] = tempList
        else:
            name = attrib.get(f"{nameSpace}name")
            childStr = ET.tostring(child, encoding="utf-8").decode('utf-8')
            tempList = getAttrList(childStr)
            if len(tempList) > 0:
                dict[name] = tempList


def getAttrList(data):
    tempList = []
    # print(data)
    matches = re.finditer(regex, data, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        type = match.group(2)
        value = match.group(3)
        tempList.append({type: value})
    return tempList


if __name__ == "__main__":
    # from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.8.76/DecodeCode/Whatsapp_v2.23.8.76"
    # to_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    mCurrentPath = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")

    args = parser.parse_args()
    from_dir = args.from_dir
    to_dir = args.to_dir

    findResMapping(f"{from_dir}/AndroidManifest.xml", f"{to_dir}/AndroidManifest.xml")
