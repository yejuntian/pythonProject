import argparse
import codecs
import glob
import json
import os
import re
import time
import traceback
import lxml.etree as ET

# 只匹配下面的文件类型
extends = ["xml", "png"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin',
             'lib', 'META-INF', 'original', 'apktool.yml']
typeMapping = {"arrays.xml": "array", "attrs.xml": "attr", "bools.xml": "bool",
               "colors.xml": "color", "dimens.xml": "dimen", "drawables.xml": "drawable",
               "integers.xml": "integer", "plurals.xml": "plurals", "strings.xml": "string",
               "styles.xml": "style"}
# 保留文件后缀集合
# keepFileSuffixList = ["anim", "animator", "color", "interpolator", "xml"]
# 三方sdk中含有的属性
sdkDict = {}
# 是否排除sdk属性方便APKTOOL_DUMMYVAL_xxx 属性的还原操作
excludeSDKAttr = False
# 保存所有public属性对应关系
publicAttrList = []
# 用来保存重命名中冲突的属性Name集合
repeatAttrName = set()

"""
    主要作用：加载scripts/values/replace_layout/mapping.json文件，
    排除sdk中R$*smali的资源属性后，根据对应关系对res目录下xml资源属性进行重命名。
"""


def replaceRes(from_dir):
    beforeTime = time.time()
    parserPublicXML(f"{from_dir}/res/values/public.xml")
    # 排除sdk中的属性，不需要重命名
    attrDict = getSmaliAttr()
    mappingData = loadData(f"{mCurrentPath}/scripts/values/replace_layout/mapping.json")
    # mappingData = loadData(f"mapping.json")
    newMappingData = getFilterMappingData(attrDict, mappingData)
    # print(newMappingData)
    transFolder(from_dir, blacklist, newMappingData)
    if len(sdkDict) > 0:
        print("\n****************不需要混淆的sdk属性如下****************")
        print(sdkDict)
    if len(repeatAttrName) > 0:
        print("\n****************重命名中冲突的属性如下****************")
        print(repeatAttrName)
    afterTime = time.time()
    print(f"\n程序执行完毕，输出结果保存到：{from_dir} 共耗时{afterTime - beforeTime} 秒")


# 排除掉attrDict集合中的属性
def getFilterMappingData(attrDict, mappingData):
    newMappingData = {}
    for attrType, attrList in mappingData.items():
        if sdkDict.get(attrType) is None:
            sdkDict[attrType] = []
        resList = attrDict.get(attrType)
        for attrNameDict in attrList:
            for oldName, newName in attrNameDict.items():
                if resList is None:
                    newMappingData[f"{oldName}#{attrType}"] = f"{newName}#{attrType}"
                else:
                    if excludeSDKAttr:  # 忽略sdk属性
                        newMappingData[f"{oldName}#{attrType}"] = f"{newName}#{attrType}"
                    else:
                        if oldName not in resList:
                            newMappingData[f"{oldName}#{attrType}"] = f"{newName}#{attrType}"
                        else:  # 去重并添加不需要混淆的属性
                            if attrNameDict not in sdkDict[attrType]:
                                sdkDict[attrType].append(attrNameDict)
    return newMappingData


def parserPublicXML(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrType = attrib.get("type")
        if attrName is not None and attrType is not None:
            newAttrName = f"{attrName}#{attrType}"
            if newAttrName not in publicAttrList:
                publicAttrList.append(newAttrName)


# 获取smali文件所有属性
def getSmaliAttr():
    attrDict = {}
    file_list = glob.glob(pathname=from_dir + "/**/R$*smali", recursive=True)
    if len(file_list) <= 0: return
    for fpath in file_list:
        fileName = os.path.basename(fpath)
        attrType = fileName.split(".")[0].split("$")[-1]
        if fileName == "R$styleable.smali":
            continue
        if attrDict.get(attrType) is None:
            attrDict[attrType] = []
        with open(fpath, encoding="utf-8", mode="r") as rf:
            lines = rf.readlines()
            for line in lines:
                if line.startswith(".field public static final"):
                    attrName = line.split(":")[0].split(" ")[-1].strip()
                    if attrType == "style":
                        attrName = attrName.replace("_", ".")
                    if attrName not in attrDict.get(attrType):
                        attrDict[attrType].append(attrName)
    return attrDict


# 获取public.xml 属性id和属性name映射关系
def getPublicMapping(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    mappingData = {}
    for child in root:
        attrib = child.attrib
        name = attrib.get("name")
        id = attrib.get("id")
        type = attrib.get("type")
        if name is None or id is None:
            continue
        if type == "style" and name.__contains__("."):
            name = name.replace(".", "_")
        mappingData[id] = name
    return mappingData


def loadData(fpath):
    with codecs.open(fpath, "r", "utf-8") as rf:
        return json.loads(rf.read())


def transFolder(from_dir, blacklist, mappingData):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if fname in blacklist:
            continue
        if os.path.isdir(fpath):
            transFolder(fpath, blacklist, mappingData)
        elif os.path.isfile(fpath):
            if fname.split(".")[-1] in extends:
                print(fpath)
                parentFolder = os.path.dirname(fpath)
                parent = parentFolder[parentFolder.rindex("/") + 1:]
                parentType = parent
                if parent.__contains__("-"):
                    parentType = parent.split("-")[0]
                isValuesDir = parent.startswith("values")
                replaceString(fpath, from_dir, mappingData, isValuesDir, fname, parentType)


def replaceString(fpath, from_dir, mappingData, isValuesDir, fname, parentType):
    if isValuesDir:  # 替换values目录文件
        renameValues(fpath, mappingData, fname)
    else:  # 替换除values目录其他文件,包括xml文件重命名操作
        if fname.split(".")[-1].endswith("xml"):
            replaceOthers(fpath, from_dir, mappingData, fname, parentType)
        else:  # 重命名png文件
            renameFile(fpath, from_dir, mappingData, fname, parentType)


# 重命名文件名称，替换文件内容
def replaceOthers(fpath, from_dir, mappingData, fname, parentType):
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = rf.read()
    with codecs.open(fpath, "w", "utf-8") as wf:
        dataTuple = getReplaceXMLContent(mappingData, data)
        print(r'替换次数：', dataTuple[1])
        wf.write(dataTuple[0])
        renameFile(fpath, from_dir, mappingData, fname, parentType)


# 重命名文件
def renameFile(fpath, from_dir, mappingData, fname, parentType):
    # 重命名file
    fileKey = f'{fname.split(".")[0]}#{parentType}'
    fileSuffix = fname[len(fname.split(".")[0]):]
    if fileKey in mappingData.keys():
        newFileName = mappingData.get(fileKey).split("#")[0]
        newPath = os.path.join(from_dir, f"{newFileName}{fileSuffix}")
        os.rename(fpath, newPath)
        print(f"fileKey = {fileKey} fileSuffix = {fileSuffix} newPath = {newPath}")


# 替换xml正则匹配内容
def getReplaceXMLContent(mappingData, data):
    replace_times = 0
    # 正则匹配"@layout/rc_tab_oneui"格式的字符串
    regex = r"\"@(\w+)\/(.*?)\""
    matches = re.finditer(regex, data, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        replaceKey = f'{match.group()}'
        type = match.group(1)
        name = match.group(2)
        key = f"{name}#{type}"
        value = mappingData.get(key)
        if value is not None:
            replaceValue = f'"@{type}/{value.split("#")[0]}"'
            # print(f"replaceKey = {replaceKey} replaceValue = {replaceValue}")
            data = data.replace(replaceKey, replaceValue)
            replace_times += 1
    # 正则匹配whatsapp:elevation="0.0dip"格式的字符串
    regex2 = r"(app|whatsapp|tools|custom):(\w+)=\".*?\""
    matches = re.finditer(regex2, data, re.MULTILINE)
    for matchNum, match2 in enumerate(matches, start=1):
        type2 = match2.group(1)
        name2 = match2.group(2)
        key2 = f"{name2}#attr"
        value2 = mappingData.get(key2)
        if value2 is not None:
            replaceKey2 = f'{type2}:{name2}='
            replaceValue2 = f'{type2}:{value2.split("#")[0]}='
            # print(f"replaceKey2 = {replaceKey2} replaceValue2 = {replaceValue2}")
            data = data.replace(replaceKey2, replaceValue2)
            replace_times += 1
    # 正则匹配="?actionBarSize"格式的字符串
    regex3 = r"=\"\?(\w+)\""
    matches = re.finditer(regex3, data, re.MULTILINE)
    for matchNum, match3 in enumerate(matches, start=1):
        name3 = match3.group(1)
        key3 = f"{name3}#attr"
        value3 = mappingData.get(key3)
        if value3 is not None:
            replaceKey3 = f'"?{name3}"'
            replaceValue3 = f'"?{value3.split("#")[0]}"'
            # print(f"replaceKey3 = {replaceKey3} replaceValue3 = {replaceValue3}")
            data = data.replace(replaceKey3, replaceValue3)
            replace_times += 1
    # 正则匹配="?attr/colorPrimary"格式的字符串
    regex4 = r"=\"\?(\w+)\/(.*)\""
    matches = re.finditer(regex4, data, re.MULTILINE)
    for matchNum, match4 in enumerate(matches, start=1):
        type4 = match4.group(1)
        name4 = match4.group(2)
        key4 = f"{name4}#{type4}"
        value4 = mappingData.get(key4)
        if value4 is not None:
            replaceKey4 = f'"?{type4}/{name4}"'
            replaceValue4 = f'"?{type4}/{value4.split("#")[0]}"'
            # print(f"replaceKey4 = {replaceKey4} replaceValue4 = {replaceValue4}")
            data = data.replace(replaceKey4, replaceValue4)
            replace_times += 1
    return data, replace_times


def renameValues(fpath, mappingData, fname):
    if fname == "public.xml":
        replaceName(mappingData, fpath, isPublicXml=True)
    else:
        if typeMapping.get(fname) is None:
            return
        else:
            attrType = typeMapping.get(fname)
            match fname:
                case "arrays.xml":
                    replaceArrays(mappingData, fpath, attrType)
                case "attrs.xml":
                    replaceName(mappingData, fpath, attrType)
                case "bools.xml":
                    replaceName(mappingData, fpath, attrType)
                case "colors.xml":
                    replaceNameAndText(mappingData, fpath, attrType)
                case "dimens.xml":
                    replaceNameAndText(mappingData, fpath, attrType)
                case "drawables.xml":
                    replaceNameAndText(mappingData, fpath, attrType)
                case "integers.xml":
                    replaceName(mappingData, fpath, attrType)
                case "plurals.xml":
                    replaceName(mappingData, fpath, attrType)
                case "strings.xml":
                    replaceNameAndText(mappingData, fpath, attrType)
                case "styles.xml":
                    replaceStyles(mappingData, fpath, attrType)


# 替换styles.xml
def replaceStyles(mappingData, fpath, attrType):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrParent = attrib.get("parent")
        if attrName is None:
            continue
        # 属性name重命名
        newAttrName = mappingData.get(f"{attrName}#{attrType}")
        if newAttrName is not None:
            # print(f"attrName = {attrName} newAttrName = {newAttrName}")
            attrib["name"] = newAttrName.split("#")[0]
        # 属性parent重命名
        if attrParent is not None:
            replaceStyleParent(attrParent, child, mappingData)
        for subChild in child:
            subChildAttrib = subChild.attrib
            subChildAttrName = subChildAttrib.get("name")
            regex = r"\"android:.*?\""
            if subChildAttrName is not None and not re.match(regex, subChildAttrName):
                # 属性name重命名
                newSubChildAttrName = mappingData.get(f"{subChildAttrName}#attr")
                if newSubChildAttrName is not None:
                    subChildAttrib["name"] = newSubChildAttrName.split("#")[0]
            replaceText(subChild.text, subChild, mappingData)
    xml_content = convert_str(root)
    # 合并其他string.xml
    save_2_file(xml_content.replace('&gt;', '>'), fpath)


# 替换style属性parent
def replaceStyleParent(xmlText, child, mappingData):
    # 匹配符合@style/Widget.AppCompat.ActionButton格式的字符串
    regex = r"(@(\w+)/(.*))"
    if re.match(regex, xmlText):
        matches = re.finditer(regex, xmlText, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            attrType = match.group(2)
            attrTxt = match.group(3)
            attrText = mappingData.get(f"{attrTxt}#{attrType}")
            # print(f"{attrTxt}#{attrType}")
            if attrText is not None:
                newTxt = f'@{attrType}/{attrText.split("#")[0]}'
                child.attrib["parent"] = str(xmlText).replace(xmlText, newTxt)


# xml文件替换属性name和文本内容
def replaceNameAndText(mappingData, fpath, attrType):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrText = child.text
        if attrName is None:
            continue
            # 属性name重命名
        newAttrName = mappingData.get(f"{attrName}#{attrType}")
        if newAttrName is not None:
            # print(f"attrName = {attrName} newAttrName = {newAttrName}")
            attrib["name"] = newAttrName.split("#")[0]
        # 替换xml内容
        replaceText(attrText, child, mappingData)
    xml_content = convert_str(root)
    # 合并其他string.xml
    save_2_file(xml_content, fpath)


# xml文件，只替换属性name
def replaceName(mappingData, fpath, attrType=None, isPublicXml=False):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        if attrName is None:
            continue
        if isPublicXml:  # public.xml
            type = attrib.get("type")
            oldAttrName = f"{attrName}#{type}"
            newAttrName = mappingData.get(oldAttrName)
            if newAttrName is not None:
                # 判断public.xml是否存在重复属性，不存在则重命名
                if not isRepeatAttrName(newAttrName):
                    print(f"newAttrName1 = {newAttrName}")
                    attrib["name"] = newAttrName.split("#")[0]
        else:
            newAttrName = mappingData.get(f"{attrName}#{attrType}")
            if newAttrName is not None:
                print(f"newAttrName2 = {newAttrName}")
                attrib["name"] = newAttrName.split("#")[0]
    xml_content = convert_str(root)
    # 合并其他string.xml
    save_2_file(xml_content, fpath)


# 判断 public.xml是否存在重名的属性，如果重名则添加到repeatAttrName集合中,否则添加到publicAttrSet集合中
def isRepeatAttrName(attrName):
    print("tt_wriggle_union#drawable" in publicAttrList)
    isRepeatName = attrName in publicAttrList
    if isRepeatName:
        # 防止重复添加属性Name
        if attrName not in repeatAttrName:
            repeatAttrName.add(attrName)
        return True
    else:
        # publicAttrSet集合中添加public.xml重命名的属性
        publicAttrList.append(attrName)
        return False


# 替换arrays.xml
def replaceArrays(mappingData, fpath, attrType):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        if attrName is None:
            continue
        # 属性name重命名
        newAttrName = mappingData.get(f"{attrName}#{attrType}")
        if newAttrName is not None:
            # print(f"attrName = {attrName} newAttrName = {newAttrName}")
            attrib["name"] = newAttrName.split("#")[0]
        for subChild in child:
            replaceText(subChild.text, subChild, mappingData)
    xml_content = convert_str(root)
    # 合并其他string.xml
    save_2_file(xml_content, fpath)


# 替换xml内容
def replaceText(xmlText, child, mappingData):
    # 匹配符合@drawable/ic_menu格式的字符串
    regex = r"(@(\w+)/([\w.]+).*)"
    if xmlText is not None and re.match(regex, xmlText):
        matches = re.finditer(regex, xmlText, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            attrType = match.group(2)
            attrTxt = match.group(3)
            attrText = mappingData.get(f"{attrTxt}#{attrType}")
            # print(f"{attrTxt}#{attrType}")
            if attrText is not None:
                newTxt = f'@{attrType}/{attrText.split("#")[0]}'
                child.text = str(xmlText).replace(xmlText, newTxt)
    # 匹配符合?settingsTitleTextColor格式的字符串，排除以 "android:" 开头的情况
    regex2 = r"\?(?!android:)(\w+)"
    if xmlText is not None and re.match(regex2, xmlText):
        matches = re.finditer(regex2, xmlText, re.MULTILINE)
        for matchNum, match2 in enumerate(matches, start=1):
            name = match2.group(1)
            attrText2 = mappingData.get(f"{name}#attr")
            # print(f"{attrText2}#attr")
            if attrText2 is not None:
                newTxt2 = f'?{attrText2.split("#")[0]}'
                child.text = str(xmlText).replace(xmlText, newTxt2)


def convert_str(to_root):
    xml_content: str = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    sum = len(to_root)
    for index, child in enumerate(to_root):
        attr_tag = child.tag
        text = child.text
        xml_content += "    "
        # string/plurals标签中text内容">"会被转移为'&gt'
        if (attr_tag == "string" and str(text).__contains__(">")) or attr_tag == "plurals":
            child_str = ET.tostring(child, encoding="utf-8").decode('utf-8').strip().replace('&gt;', '>')
            xml_content += child_str
        else:
            xml_content += ET.tostring(child, encoding='utf-8').decode('utf-8').strip().replace('/>', ' />')
        if index < sum - 1:
            xml_content += '\n'

    xml_content += '\n</resources>\n'
    return xml_content.replace('&gt;', '>')


def save_2_file(data_str, target_file_path):
    try:
        with open(target_file_path, 'w+') as f:
            f.write(data_str)
    except Exception as result:
        print(f"写入{target_file_path}出现异常: {result}")
        print(traceback.format_exc())


if __name__ == "__main__":
    mCurrentPath = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.8.76/DecodeCode/Whatsapp_v2.23.8.76"
    replaceRes(from_dir)
