import argparse
import ast
import codecs
import json
import os
import re
import xml.etree.ElementTree as ET

# 正则匹配public.xml attr属性
matchAttrRes = r"(app|whatsapp):(\w+)=\".*?\""
# 正则匹配android:orientation="vertical"
matchAttrRes2 = r"\w+:(\w+)=\".*?\""
# 正则匹配属性="?APKTOOL_DUMMYVAL_0x7f0400ec"
matchAttrRes3 = r"=\"\?(\w+)\""
# 只匹配下面的文件类型
extends = ["xml"]
# 所有属性对应关系集合
dictList = {}
# 匹配属性集合列表
typeList = ["array", "attr", "bool", "color", "dimen", "integer", "string", "style"]
typeStr = f"{{}}#{{}}"
typeDict = {"array": typeStr, "attr": typeStr, "bool": typeStr, "color": typeStr,
            "dimen": typeStr, "integer": typeStr, "string": typeStr, "style": typeStr}

"""
    主要作用：映射typeList集合中每个属性的对应关系，查找to_dir/res/layout目录下所有未混淆的layout资源文件，
    匹配from_dir/res目录下对应的layout,正则校验如果匹配的个数相同则代表匹配成功,最终保存到layoutAttrMapping.json文件。
"""


def findAttr(from_dir, to_dir):
    allLayouts = []
    loadLayouts(f"{to_dir}/res/layout", allLayouts)
    for attrType in typeList:
        strList = typeDict[attrType].split("#")
        fromAttrsDict = json.loads(strList[0])
        toAttrsDict = json.loads(strList[0])
        resStr = fr"=\"@{attrType}/(.*?)\""
        matchMapping(from_dir, to_dir, allLayouts, fromAttrsDict, toAttrsDict, attrType, resStr)
    save2File(dictList, f"{currentPath}/scripts/values/matchStyles/layoutAttrMapping.json")


# 匹配layout xml属性对应关系
def matchMapping(from_dir, to_dir, allLayouts, fromDict, toDict, attrStyle, resStr):
    matchLayoutAttr(f"{from_dir}/res/layout", allLayouts, fromDict, attrStyle, resStr)
    matchLayoutAttr(f"{to_dir}/res/layout", allLayouts, toDict, attrStyle, resStr)
    # 加载from_dir, to_dir对应的属性集合；匹配属性的对应关系
    fromList = loadFromPublicAttrs(f"{from_dir}/res/values/public.xml", attrStyle)
    toList = loadFromPublicAttrs(f"{to_dir}/res/values/public.xml", attrStyle)
    attrMapping = getMatchAttrData(fromDict, fromList, toDict, toList, attrStyle)
    dictList[attrStyle] = attrMapping


# 匹配attr属性对应关系
def getMatchAttrData(fromAttrsDict, fromAttrList, toAttrsDict, toAttrList, attrStyle):
    attrMapping = {}
    for layoutName, toAttr in toAttrsDict.items():
        toNameList = toAttr[0][attrStyle].split("#")
        toAttrCount = toNameList[-1]
        if fromAttrsDict.get(layoutName) is None:
            continue
        fromAttr = fromAttrsDict.get(layoutName)
        fromNameList = fromAttr[0][attrStyle].split("#")
        fromAttrCount = fromNameList[-1]
        if toAttrCount == fromAttrCount and int(toAttrCount) > 0:
            print(f"layoutName = {layoutName} fromAttrCount = {fromAttrCount} toAttrCount = {toAttrCount}")
            toList = ast.literal_eval(toNameList[0])
            fromList = ast.literal_eval(fromNameList[0])
            for index in range(0, len(toList)):
                toAttrName = toList[index]
                fromAttrName = fromList[index]
                if toAttrName in toAttrList and fromAttrName in fromAttrList:
                    # 避免一个key映射多个value情况，并且混淆key为APKTOOL_DUMMYVAL_0x7f开始的属性值
                    if not fromAttrName in attrMapping.values() and toAttrName.startswith(
                            "APKTOOL_DUMMYVAL_0x7f") and not fromAttrName in toAttrList:
                        # attrMapping[f"{layoutName}#{toAttrName}"] = fromAttrName
                        attrMapping[toAttrName] = fromAttrName
    return attrMapping


# 匹配正则的字符串
def matchLayoutAttr(from_dir, allLayouts, attrsDict, attrStyle, resStr):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath):
            matchLayoutAttr(fpath, allLayouts, attrsDict, attrStyle, resStr)
        elif os.path.isfile(fpath):
            if fname.split(".")[-1] in extends and fname in allLayouts:
                print(f"fpath = {fpath} attrStyle = {attrStyle}")
                with codecs.open(fpath, "r", "utf-8") as rf:
                    data = rf.read()
                    # 正则匹配matchAttrRes属性
                    attrStyleDict = {}
                    if attrsDict.get(fname) is None:
                        attrsDict[fname] = []
                    if attrStyleDict.get(attrStyle) is None:
                        attrStyleDict[attrStyle] = {}
                    searchAttrList = []
                    if attrStyle == "attr":
                        searchAttrList.extend(getMatchAttrList(matchAttrRes, data, 2))
                        # 正则匹配matchAttrRes3属性
                        searchAttrList.extend(getMatchAttrList(matchAttrRes3, data, 1))
                    else:
                        searchAttrList = getMatchAttrList(resStr, data, 1)
                attrStyleDict[attrStyle] = f"{searchAttrList}#{len(searchAttrList)}"
                # print(f"resStr = {resStr} attrStyle = {attrStyle} attrStyleDict ={attrStyleDict}")
                attrsDict[fname].append(attrStyleDict)


# 正则匹配
def getMatchAttrList(resStr, data, groupIndex):
    searchAttrList = []
    matchDimens = re.finditer(resStr, data, re.MULTILINE)
    for matchNum, match in enumerate(matchDimens, start=1):
        dimenName = match.group(groupIndex)
        searchAttrList.append(dimenName)
    return searchAttrList


# 加载public.xml所有属性
def loadFromPublicAttrs(fpath, attrStyle):
    parse = ET.parse(fpath)
    root = parse.getroot()
    attrList = []
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrType = attrib.get("type")
        if not attrName is None and not attrType is None:
            if attrType == attrStyle:
                attrList.append(attrName)
    return attrList


# 加载所有layout.xml
def loadLayouts(fromDir, layoutList):
    listdir = os.listdir(fromDir)
    for fname in listdir:
        fpath = os.path.join(fromDir, fname)
        if os.path.isdir(fpath):
            loadLayouts(fpath, layoutList)
        else:
            if not fname.startswith("APKTOOL_DUMMYVAL"):
                layoutList.append(fname)


def save2File(dataList, fileName):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,结果保存到：{os.path.join(os.getcwd(), fileName)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    to_dir = args.to_dir
    # from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    # to_dir = "/Users/shareit/work/GBWorke/whatsapp_new/Whatsapp_v2.22.24.78"
    currentPath = os.getcwd()
    findAttr(from_dir, to_dir)
