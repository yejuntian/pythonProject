import argparse
import codecs
import json
import os
import re
import xml.etree.ElementTree as ET

# 排除哪些文件夹
blacklist = ['.idea', '.git', '.gradle', 'kotlin', 'lib', 'META-INF', 'original', 'apktool.yml']
# 寻找符合android:id="@id/eula_title"格式的正则
matchRes = r"\"@\w+\/.*?\""
# 寻找styles.xml符合<item name="android:src">@drawable/ic_menu</item>格式的正则
matchRes2 = r">(@\w+/(\w+).*)<"
# 匹配public.xml attr属性正则
matchAttrRes = r"(app|whatsapp|tools|custom):(\w+)=\".*?\""
# 匹配属性正则="?APKTOOL_DUMMYVAL_0x7f0400ec"
matchAttrRes3 = r"=\"\?(\w+)\""
# 匹配属性正则=>?APKTOOL_DUMMYVAL_0x7f040432</item>
matchAttrRes4 = r">(\?(\w+))<"
# 匹配属性="?android:textAppearanceMedium"
matchAttrRes5 = r"=\"\?(\w+):(.*?)\""
# 只匹配下面的文件类型
extends = ["xml"]

"""
    主要作用：校验res目录下所有的xml属性样式是否存在（eg:"@id/conversations_row_ephemeral_status"）
"""


def checkLayout(from_dir, to_dir):
    # 获取layout xml布局中所有以"@id/\w+"格式的属性
    allValues = set()
    findValues(from_dir, allValues)
    mappingData = getValuesMapping(allValues)
    matchValues(f"{to_dir}/res/values/public.xml", mappingData)


def matchValues(fpath, mappingData):
    parse = ET.parse(fpath)
    root = parse.getroot()
    public_dict = {}
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrType = attrib.get("type")
        if attrName is None:
            continue
        if public_dict.get(attrType) is None:
            public_dict[attrType] = []
        public_dict[attrType].append(attrName)

    # 查询没有匹配的属性值
    temp_dict = {}
    for attrType, nameList in mappingData.items():
        # 创建映射关系集合对象
        if temp_dict.get(attrType) is None:
            temp_dict[attrType] = []
        # 匹配属性name
        attrNameList = public_dict.get(attrType)
        if attrNameList is None:
            continue
        for attrName in nameList:
            if not attrName in attrNameList:
                temp_dict[attrType].append(attrName)

    # 没有找到的属性保存到NotFind.json文件中
    isFind = False
    for type, typeList in temp_dict.items():
        if len(typeList) > 0:
            isFind = True
            break
    if isFind:
        save2File(temp_dict, "scripts/values/native_values/GBNeedToFind.json")
    else:
        print("程序执行结束，所有属性完全匹配！")


def save2File(dataList, fpath):
    dirName = os.path.dirname(fpath)
    if not os.path.exists(dirName):
        os.makedirs(dirName, exist_ok=True)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fpath, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,未找到的属性保存到：{os.path.join(os.getcwd(), fpath)}")


def getPublicMapping(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    public_dict = {}
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrType = attrib.get("type")
        if attrName is None:
            continue
        if public_dict.get(attrType) is None:
            public_dict[attrType] = []
        public_dict[attrType].append(attrName)
    return public_dict


def findValues(from_dir, allValues):
    if os.path.isdir(from_dir):
        listdir = os.listdir(from_dir)
        for fname in listdir:
            if not fname in blacklist:
                fpath = os.path.join(from_dir, fname)
                if os.path.isdir(fpath):
                    findValues(fpath, allValues)
                elif os.path.isfile(fpath):
                    if fname.split(".")[-1] in extends:
                        print(fpath)
                        addValues(fpath, allValues)
    else:
        addValues(from_dir, allValues)


def addValues(fpath, allValues):
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = rf.read()
        # 正则匹配matchRes属性
        matches = re.finditer(matchRes, data, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            allValues.add(match.group())
            # print(match.group())
        # 正则匹配matchRes2属性
        matches = re.finditer(matchRes2, data, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            allValues.add(f'"{match.group(1)}"')
            # print(f'"{match.group(1)}"')
        # 正则匹配matchAttrRes属性
        matchAttrs = re.finditer(matchAttrRes, data, re.MULTILINE)
        for matchNum, match in enumerate(matchAttrs, start=1):
            attrName = match.group(2)
            allValues.add(f'"@attr/{attrName}"')
        # 正则匹配matchAttrRes3属性
        matchAttrs = re.finditer(matchAttrRes3, data, re.MULTILINE)
        for matchNum, match in enumerate(matchAttrs, start=1):
            attrName = match.group(1)
            allValues.add(f'"@attr/{attrName}"')
            # print(f'"matchAttrRes3 = @attr/{attrName}"')
        # 正则匹配matchAttrRes4属性
        matchAttrs = re.finditer(matchAttrRes4, data, re.MULTILINE)
        for matchNum, match in enumerate(matchAttrs, start=1):
            attrName = match.group(2)
            allValues.add(f'"@attr/{attrName}"')
            # print(f'"matchAttrRes4 = @attr/{attrName}"')


def getValuesMapping(allValues):
    regex = r"\"@(\w+)\/(.*?)\""
    valuesDict = {}
    for value in allValues:
        matches = re.finditer(regex, value, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            type = match.group(1)
            name = match.group(2)
            # print(f"value = {value} type = {type} name = {name}")
            if valuesDict.get(type) is None:
                valuesDict[type] = []
            valuesDict[type].append(name)
    return valuesDict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_dir")
    args = parser.parse_args()

    # folder_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.22.24.78/res"
    folder_dir = f"{args.folder_dir}/res"
    to_dir = folder_dir[0:folder_dir.index("/res")]
    checkLayout(args.folder_dir, to_dir)
