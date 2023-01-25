import codecs
import json
import os
import re
import traceback

import lxml.etree as ET

# 只匹配下面的文件类型
extends = ["xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin',
             'lib', 'META-INF', 'original', 'apktool.yml']
typeMapping = {"arrays.xml": "array", "attrs.xml": "attr", "bools.xml": "bool",
               "colors.xml": "color", "dimens.xml": "dimen", "drawables.xml": "drawable",
               "integers.xml": "integer", "plurals.xml": "plurals", "strings.xml": "string",
               "styles.xml": "style"}


def replaceRes(fpath):
    mappingData = loadData("mapping.json")
    transFolder(fpath, blacklist, mappingData)


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
    replace_times = 0
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = rf.read()
    with codecs.open(fpath, "w", "utf-8") as wf:
        for name, value in mappingData.items():
            key = name.split("#")[0]
            typeSplit = value.split("#")
            type = typeSplit[-1]
            newKey = f'"@{type}/{key}"'
            newValue = f'"@{type}/{typeSplit[0]}"'
            # 重命名file
            if key == fname.split(".")[0] and parentType == type:
                enableRenameFile = True
                newPath = os.path.join(from_dir, typeSplit[0])
        replace_times += data.count(newKey)
        data = data.replace(newKey, newValue)
        print(r'替换次数：', replace_times)
        wf.write(data)
        if enableRenameFile:
            os.rename(fpath, newPath)


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
                    replaceName(mappingData, fpath, attrType)
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
    regex = r"(@(\w+)/(\w+).*)"
    if re.match(regex, xmlText):
        matches = re.finditer(regex, xmlText, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            attrType = match.group(2)
            attrTxt = match.group(3)
            attrText = mappingData.get(f"{attrTxt}#{attrType}")
            # print(f"{attrTxt}#{attrType}")
            if not attrText is None:
                newTxt = f'@{attrType}/{attrText.split("#")[0]}'
                child.text = str(xmlText).replace(xmlText, newTxt)


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
