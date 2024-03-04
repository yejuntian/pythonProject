import os
import glob
import codecs
import xml.etree.ElementTree as ET
import re
import json

# 保存public.xml属性集合
attrTypeNameList = {}
# 所有未注册的属性集合
allAttrs = {}
# 遍历所有的xml，对需要注入public.xml的属性进行二次校验,防止注入不存的属性
xmlList = {"string": "strings.xml", "dimen": "dimens.xml",
           "integer": "integers.xml", "array": "arrays.xml",
           "style": "styles.xml", "attr": "attrs.xml",
           "color": "colors.xml", "id": "ids.xml"}
# 用于存放注入属性的集合
checkAttrDict = {}
# 用于存放没有找到的属性
notFindAttrDict = {}
# 需要特殊处理的样式
spacialTypeList = ["style", "dimen"]
attrType = ["style", "drawable", "color", "attr", "bool", "dimen"]

"""
    主要作用:查找所有sdk中attrType集合中所有未注册的属性，保存到addValuesRegister/sdkAttr.json文件中。
    from_dir:参考项目
    to_dir:目标项目
"""


def findAllAttrs(from_dir, to_dir):
    getCheckAttrDic(f"{from_dir}/res")
    parserPublic(f"{to_dir}/res/values/public.xml")
    filterAttrs(from_dir)


# 获取xml属性集合
def getCheckAttrDic(from_dir):
    for type, fname in xmlList.items():
        if checkAttrDict.get(type) is None:
            checkAttrDict[type] = []
        if notFindAttrDict.get(type) is None:
            notFindAttrDict[type] = []
        xmlPathList = glob.glob(pathname=f"{from_dir}/**/{fname}", recursive=True)
        for path in xmlPathList:
            parser = ET.parse(path)
            root = parser.getroot()
            for child in root:
                attrib = child.attrib
                attrName = attrib.get("name")
                if attrName is not None and attrName not in checkAttrDict.get(type):
                    checkAttrDict[type].append(attrName)


def filterAttrs(from_dir):
    filePathList = glob.glob(pathname=from_dir + "/**/R$*smali", recursive=True)
    styleNameList = checkAttrDict.get(spacialTypeList[0])
    dimenNameList = checkAttrDict.get(spacialTypeList[1])
    for fpath in filePathList:
        fileName = os.path.basename(fpath)
        if fileName == "R$styleable.smali":
            continue
        fileType = fpath.split("$")[1].split(".")[0]
        if allAttrs.get(fileType) is None:
            allAttrs[fileType] = []

        with codecs.open(fpath, encoding="utf-8", mode="r") as rf:
            lines = rf.readlines()
            for line in lines:
                if line.startswith(".field public static"):
                    attrName = line.split(":")[0].split(" ")[-1]
                    # style/dimen样式特殊处理，进行重命名操作
                    attrName = getSpecialTypeName(fileType, attrName, styleNameList, dimenNameList)
                    if attrName is not None and attrName not in attrTypeNameList.get(fileType) \
                            and attrName not in allAttrs.get(fileType) and fileType in attrType:
                        allAttrs[fileType].append(attrName)

    save2File(allAttrs, f"{os.getcwd()}/sdkAttr.json")


# style/dimen样式需要特殊处理
def getSpecialTypeName(fileType, attrName, styleNameList, dimenNameList):
    if fileType == "style":
        if attrName.replace("_", ".") in styleNameList:
            attrName = attrName.replace("_", ".")
        elif attrName.replace(".", "_") in styleNameList:
            attrName = attrName.replace(".", "_")
    elif fileType == "dimen":
        regex = r"(.*common_dimens_)(\d+[_.]\d+dp)"
        if re.match(regex, attrName):
            matches = re.finditer(regex, attrName, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                preName = match.group(1)
                lastName = match.group(2)
                tempAttrName = f"{preName}{lastName.replace('_', '.')}"
                # print(f"newDimenName = {tempAttrName}  preDimenName = {attrName}")
                if tempAttrName in dimenNameList:
                    attrName = tempAttrName
    return attrName


def save2File(dataList, fpath):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，文件保存在:{fpath}")


def parserPublic(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrType = attrib.get("type")
        attrName = attrib.get("name")
        if attrType is None or attrName is None:
            continue
        if attrTypeNameList.get(attrType) is None:
            attrTypeNameList[attrType] = []
        if attrName not in attrTypeNameList.get(attrType):
            attrTypeNameList[attrType].append(attrName)


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.3.81/DecodeCode/Whatsapp_v2.24.3.81"
    to_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.7.79/DecodeCode/Whatsapp_v2.24.7.79"
    findAllAttrs(from_dir, to_dir)
