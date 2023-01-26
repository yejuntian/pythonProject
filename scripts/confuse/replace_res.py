import codecs
import glob
import json
import os
import lxml.etree as ET
import re
import traceback

# 只匹配下面的文件类型
extends = ["xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin',
             'lib', 'META-INF', 'original', 'apktool.yml']
typeMapping = {"arrays.xml": "array", "attrs.xml": "attr", "bools.xml": "bool",
               "colors.xml": "color", "dimens.xml": "dimen", "drawables.xml": "drawable",
               "integers.xml": "integer", "plurals.xml": "plurals", "strings.xml": "string",
               "styles.xml": "style"}
# 保留文件后缀集合
keepFileSuffixList = ["anim", "animator", "color", "interpolator", "xml"]


def replaceRes(from_dir):
    mappingData = loadData("mapping.json")
    transFolder(from_dir, blacklist, mappingData)
    replaceSmaliAttrName(from_dir)


# 替换R$*.smali 属性名
def replaceSmaliAttrName(from_dir):
    file_list = glob.glob(pathname=from_dir + "/**/R$*smali", recursive=True)
    if len(file_list) <= 0: return
    mappingData = getPublicMapping(f"{from_dir}/res/values/public.xml")
    for fpath in file_list:
        replaceSmaliFile(fpath, mappingData)


def replaceSmaliFile(fpath, mappingData):
    fileName = os.path.basename(fpath)
    if fileName != "R$styleable.smali":
        data = ""
        with open(fpath, encoding="utf-8", mode="r") as rf:
            lines = rf.readlines()
            for line in lines:
                if line.startswith(".field public static final"):
                    attrId = line.split(" = ")[-1].replace("\n", "")
                    # print(f"fpath = {fpath} attrId = {attrId}")
                    attrName = mappingData[attrId]
                    data += f".field public static final {attrName}:I = {attrId}\n"
                else:
                    data += line
        with open(fpath, encoding="utf-8", mode="w") as wf:
            wf.write(data)


# 获取public.xml 属性id和属性name映射关系
def getPublicMapping(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    mappingData = {}
    for child in root:
        attrib = child.attrib
        name = attrib.get("name")
        id = attrib.get("id")
        if not name is None and name.__contains__("."):
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
    else:  # 替换除values目录其他文件
        replaceOthers(fpath, from_dir, mappingData, fname, parentType)


def replaceOthers(fpath, from_dir, mappingData, fname, parentType):
    enableRenameFile = False
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = rf.read()
    with codecs.open(fpath, "w", "utf-8") as wf:
        dataTuple = getReplaceXMLContent(mappingData, data)
        # 重命名file
        fileKey = f'{fname.split(".")[0]}#{parentType}'
        if fileKey in mappingData.keys():
            enableRenameFile = True
            newFileName = mappingData.get(fileKey).split("#")[0]
            if parentType in keepFileSuffixList:
                newPath = os.path.join(from_dir, f"{newFileName}.xml")
            else:
                newPath = os.path.join(from_dir, newFileName)
        print(r'替换次数：', dataTuple[1])
        wf.write(dataTuple[0])
        if enableRenameFile:
            os.rename(fpath, newPath)


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


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    replaceRes(from_dir)
