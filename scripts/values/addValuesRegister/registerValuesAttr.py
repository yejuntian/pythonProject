import glob
import os
import re
import codecs
import xml.etree.ElementTree as ET
import json

# 保存public.xml属性集合
attrTypeNameList = {}
# 保存没有注册的属性集合
notRegisterTypeNameList = {}
# 映射对应类型
typeList = {"strings.xml": "string", "styles.xml": "style", "colors.xml": "color",
            "bools.xml": "bool", "dimens.xml": "dimen", "integers.xml": "integer"}
# @integer/APKTOOL_DUMMYVAL_0x7f0c0020
stringRegx = r"@(\w+)/(\w+)"


def registerValues(from_dir):
    # 解析public.xml文件
    parserPublic(f"{from_dir}/res/values/public.xml")
    # 过滤出没有注册的属性
    filterNoRegisterAttrs(from_dir)
    save2File(notRegisterTypeNameList, "noRegisterAttr.json")


def save2File(dataList, fpath):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，文件保存在:{fpath}")


def filterNoRegisterAttrs(from_dir):
    filePathlist = glob.glob(f"{from_dir}/res/values*-v1/*.xml", recursive=True)
    for fpath in filePathlist:
        fname = os.path.basename(fpath)
        attrType = typeList.get(fname)
        match fname:
            case "strings.xml":
                filterCommonXml(fpath, attrType)
            case "styles.xml":
                filterStyleXml(fpath, attrType)
            case "colors.xml":
                filterCommonXml(fpath, attrType)
            case "bools.xml":
                filterCommonXml(fpath, attrType)
            case "dimens.xml":
                filterCommonXml(fpath, attrType)
            case "integers.xml":
                filterCommonXml(fpath, attrType)

        # print(f"fname = {fname} attrType = {attrType}")


# 过滤通用styles.xml
def filterStyleXml(fpath, attrType):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrParent = attrib.get("parent")
        if attrName is None:
            continue
        attrNameList = attrTypeNameList.get(attrType)
        if attrName not in attrNameList:
            addAttrNames(attrName, attrType)
        if attrParent is not None:
            # print(f"attrParent = {attrParent}")
            filterStyleParent(attrParent, attrNameList)
        # 遍历子item元素
        for subChild in child:
            sub_child_attrib = subChild.attrib
            sub_child_attrName = sub_child_attrib.get("name")
            if sub_child_attrName is None:
                continue
            attrNameList = attrTypeNameList.get("attr")
            if not sub_child_attrName.startswith("android:") and sub_child_attrName not in attrNameList:
                addAttrNames(sub_child_attrName, "attr")
            filterStyleItemText(subChild.text)


# 过滤styles.xml item元素text文本内容
def filterStyleItemText(xmlText):
    # 匹配符合@drawable/ic_menu格式的字符串
    regex = r"(@(\w+)/([\w.]+).*)"
    if xmlText is not None and re.match(regex, xmlText):
        matches = re.finditer(regex, xmlText, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            attrType = match.group(2)
            attrTxt = match.group(3)
            # print(f"{attrTxt}#{attrType}")
            attrNameList = attrTypeNameList.get(attrType)
            if attrTxt not in attrNameList:
                addAttrNames(attrTxt, attrType)
    # 匹配符合?settingsTitleTextColor格式的字符串，排除以 "android:" 开头的情况
    regex2 = r"\?(?!android:)(\w+)"
    if xmlText is not None and re.match(regex2, xmlText):
        matches = re.finditer(regex2, xmlText, re.MULTILINE)
        for matchNum, match2 in enumerate(matches, start=1):
            attrName = match2.group(1)
            if attrName is not None and attrName not in attrTypeNameList.get("attr"):
                addAttrNames(attrName, "attr")


# 过滤style属性parent
def filterStyleParent(xmlText, attrNameList):
    # 匹配符合@style/Widget.AppCompat.ActionButton格式的字符串
    regex = r"(@(\w+)/(.*))"
    if re.match(regex, xmlText):
        matches = re.finditer(regex, xmlText, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            attrType = match.group(2)
            attrName = match.group(3)
            if attrName is not None and attrName not in attrNameList:
                addAttrNames(attrName, attrType)


# 过滤通用xml
def filterCommonXml(fpath, attrType):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrText = child.text
        if attrName is None:
            continue
        nameList = attrTypeNameList.get(attrType)
        if attrName not in nameList:
            addAttrNames(attrName, attrType)
        # print(f"attrName = {attrName} attrText = {attrText}")
        if attrText is not None and re.match(stringRegx, attrText):
            matches = re.finditer(stringRegx, attrText, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                attrNewType = match.group(1)
                attrNewName = match.group(2)
                nameList = attrTypeNameList.get(attrNewType)
                if attrName not in nameList:
                    addAttrNames(attrNewName, attrNewType)


# 添加没有注册的属性到集合列表中
def addAttrNames(attrName, attrType):
    if notRegisterTypeNameList.get(attrType) is None:
        notRegisterTypeNameList[attrType] = []
    if attrName not in notRegisterTypeNameList.get(attrType):
        notRegisterTypeNameList[attrType].append(attrName)


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
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.20.76/DecodeCode/Whatsapp_v2.23.20.76"
    registerValues(from_dir)
