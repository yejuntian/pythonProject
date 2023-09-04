import codecs
import os
import re
import traceback
import lxml.etree as ET

# 只匹配下面的文件类型
extends = ["xml", "png"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'lib',
             'META-INF', 'original', 'apktool.yml']
# values文件夹映射关系
typeMapping = {"arrays.xml": "array", "attrs.xml": "attr", "bools.xml": "bool",
               "colors.xml": "color", "dimens.xml": "dimen", "drawables.xml": "drawable",
               "integers.xml": "integer", "plurals.xml": "plurals", "strings.xml": "string",
               "styles.xml": "style"}

"""
    主要作用：根据mappingData字典的对应关系对res目录下xml资源属性进行重命名。
"""


def replaceRes(from_dir, mappingData):
    newMappingData = getFilterMappingData(mappingData)
    transFolder(from_dir, blacklist, newMappingData)


# 集合中的属性
def getFilterMappingData(mappingData):
    newMappingData = {}
    for attrType, attrList in mappingData.items():
        for attrNameDict in attrList:
            for oldName, newName in attrNameDict.items():
                newMappingData[f"{oldName}#{attrType}"] = f"{newName}#{attrType}"
    return newMappingData


def transFolder(from_dir, blacklist, mappingData):
    print(from_dir)
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
        if not value is None:
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
        if not value2 is None:
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
        if not value3 is None:
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
        if not value4 is None:
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
        if not newAttrName is None:
            # print(f"attrName = {attrName} newAttrName = {newAttrName}")
            attrib["name"] = newAttrName.split("#")[0]
        # 属性parent重命名
        if not attrParent is None:
            replaceStyleParent(attrParent, child, mappingData)
        for subChild in child:
            subChildAttrib = subChild.attrib
            subChildAttrName = subChildAttrib.get("name")
            regex = r"\"android:.*?\""
            if not subChildAttrName is None and not re.match(regex, subChildAttrName):
                # 属性name重命名
                newSubChildAttrName = mappingData.get(f"{subChildAttrName}#attr")
                if not newSubChildAttrName is None:
                    subChildAttrib["name"] = newSubChildAttrName.split("#")[0]
            replaceText(subChild.text, subChild, mappingData)
    xml_content = convert_str(root)
    # 合并其他string.xml
    save_2_file(xml_content, fpath)


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
            if not attrText is None:
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
        if not newAttrName is None:
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
            newAttrName = mappingData.get(f"{attrName}#{type}")
            if not newAttrName is None:
                attrib["name"] = newAttrName.split("#")[0]
        else:
            newAttrName = mappingData.get(f"{attrName}#{attrType}")
            if not newAttrName is None:
                attrib["name"] = newAttrName.split("#")[0]
    xml_content = convert_str(root)
    # 合并其他string.xml
    save_2_file(xml_content, fpath)


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
        if not newAttrName is None:
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
    if not xmlText is None and re.match(regex, xmlText):
        matches = re.finditer(regex, xmlText, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            attrType = match.group(2)
            attrTxt = match.group(3)
            attrText = mappingData.get(f"{attrTxt}#{attrType}")
            # print(f"{attrTxt}#{attrType}")
            if not attrText is None:
                newTxt = f'@{attrType}/{attrText.split("#")[0]}'
                child.text = str(xmlText).replace(xmlText, newTxt)
    # 匹配符合?settingsTitleTextColor格式的字符串
    regex2 = r"\?(\w+)"
    if not xmlText is None and re.match(regex2, xmlText):
        matches = re.finditer(regex2, xmlText, re.MULTILINE)
        for matchNum, match2 in enumerate(matches, start=1):
            name = match2.group(1)
            attrText2 = mappingData.get(f"{name}#attr")
            # print(f"{attrText2}#attr")
            if not attrText2 is None:
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
    return xml_content


def save_2_file(data_str, target_file_path):
    try:
        with open(target_file_path, 'w+') as f:
            f.write(data_str)
    except Exception as result:
        print(f"写入{target_file_path}出现异常: {result}")
        print(traceback.format_exc())
