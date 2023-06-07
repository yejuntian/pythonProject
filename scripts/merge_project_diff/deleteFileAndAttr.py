import lxml.etree as ET
import os
import codecs
import json

"""
    主要作用：根据merge_project_diff脚本生成的diff文件，删除diff文件中无用的xml文件和属性
"""
# 需要检查并删除的文件列表
fileList = ["anim", "animator", "interpolator", "drawable", "layout", "menu", "mipmap", "raw", "xml"]
# 需要解析并校验xml内容的列表集合
typeMapping = {"arrays.xml": "array", "attrs.xml": "attr", "bools.xml": "bool",
               "colors.xml": "color", "dimens.xml": "dimen", "drawables.xml": "drawable",
               "ids.xml": "id", "integers.xml": "integer", "plurals.xml": "plurals",
               "strings.xml": "string", "styles.xml": "style"}
# public.xml映射child集合 ==》type对应child集合列表
publicMappingChildData = {}
# public.xml映射属性name集合 ==》type对应name集合列表
publicMappingNameData = {}
# 删除的文件集合
deleteFileDict = {}
# 字符串前缀
strPrefix = "APKTOOL_DUMMYVAL_"
# 属性集合
attrTypeDict = {"array": [], "attr": [], "bool": [], "color": [], "dimen": [],
                "drawable": [], "id": [], "integer": [], "plurals": [], "string": [],
                "style": [], "anim": [], "animator": [], "interpolator": [], "layout": [],
                "menu": [], "mipmap": [], "raw": [], "xml": []}


def deleteGarbage(from_dir):
    publicMapping(f"{from_dir}/res/values/public.xml", publicMappingChildData, publicMappingNameData)
    # 校验fileList结合，删除无用文件
    checkFile(f"{from_dir}/res")
    checkXMlAttr(from_dir)
    saveJsonFile(deleteFileDict, "deleteFileAndAttrs.json")


# 检查xml属性，删除无用属性
def checkXMlAttr(from_dir):
    if os.path.exists(f"{from_dir}/res/values"):
        for fName, fileType in typeMapping.items():
            # 创建对应关系
            if deleteFileDict.get(fileType) is None:
                deleteFileDict[fileType] = []
            fpath = f"{from_dir}/res/values/{fName}"
            if fileType == "style":
                parserStylesXML(fpath, fileType)
            elif fileType == "array" or fileType == "attr":
                parserArraysXML(fpath, fileType)
            elif fileType == "color" or fileType == "dimen" or fileType == "drawable":
                parserColorXML(fpath, fileType)
            else:
                parserCommonXML(fpath, fileType)

        # 遍历所有以values-tr形式的文件夹删除xml无用属性
        tranValuesFolder(from_dir)
        # 删除public.xml多余属性
        for attrType in attrTypeDict:
            deletePublicNote(attrType)
        # 重新写入public.xml文件
        save_to_publicXML(publicMappingChildData, f"{from_dir}/res/values/public.xml")


def tranValuesFolder(from_dir):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath):
            tranValuesFolder(fpath)
        elif os.path.isfile(fpath):
            if fname.startswith("plurals.xml") or fname.startswith("strings.xml") \
                    or fname.startswith("bools.xml") or fname.startswith("integers.xml") \
                    or fname.startswith("ids.xml"):
                parserCommonXML(fpath, typeMapping.get(fname))
            elif fname.startswith("colors.xml") or fname.startswith("dimens.xml") \
                    or fname.startswith("drawables.xml"):
                parserColorXML(fpath, typeMapping.get(fname))
            elif fname.startswith("styles.xml"):
                parserStylesXML(fpath, typeMapping.get(fname))
            elif fname.startswith("arrays.xml") or fname.startswith("attrs.xml"):
                parserArraysXML(fpath, typeMapping.get(fname))


# 解析arrays.xml
def parserArraysXML(fpath, fileType):
    arrayList = []
    parser = ET.parse(fpath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        if attrName is None:
            continue
        # 是否允许添加该节点标签
        enableAdd = True
        for subChild in child:
            subText = subChild.text
            if subText is not None:
                enableAdd = not subText.__contains__(strPrefix)
        # print(f"attrName = {attrName} fpath = {fpath} fileType = {fileType}")
        if not attrName.startswith(strPrefix) and attrName in publicMappingNameData.get(fileType) and enableAdd:
            arrayList.append(child)
            attrTypeDict.get(fileType).append(attrName)
        else:
            deletePublicAttrName(attrName, fileType)
            deleteFileAndAttr(attrName, fileType)
    # 重新写入xml文件
    xml_content = convert_str(arrayList)
    saveXMLfile(xml_content, fpath)


# 解析styles.xml
def parserStylesXML(fpath, fileType):
    styleList = []
    parser = ET.parse(fpath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrParent = attrib.get("parent")
        if attrName is None:
            continue
        # 是否允许添加该节点标签
        enableAdd = True
        for subChild in child:
            subAttrName = subChild.attrib.get("name")
            if subAttrName is not None and enableAdd:
                enableAdd = not subAttrName.__contains__(strPrefix)
            # 判断内容
            subText = subChild.text
            if subText is not None and enableAdd:
                enableAdd = not subText.__contains__(strPrefix)
        # 判断parent标签
        if attrParent is not None and enableAdd:
            enableAdd = not attrParent.__contains__(strPrefix)
        # print(f"attrName = {attrName} fpath = {fpath} fileType = {fileType}")
        if not attrName.startswith(strPrefix) and attrName in publicMappingNameData.get(fileType) and enableAdd:
            styleList.append(child)
            attrTypeDict.get(fileType).append(attrName)
        else:
            deletePublicAttrName(attrName, fileType)
            deleteFileAndAttr(attrName, fileType)
    # 重新写入xml文件
    xml_content = convert_str(styleList)
    saveXMLfile(xml_content, fpath)


# 删除public.xml注册的多余标签
def deletePublicNote(fileType):
    attrNameList = attrTypeDict.get(fileType)
    nameList = publicMappingNameData.get(fileType)
    # print(f"fileType = {fileType} attrNameList = {attrNameList} nameList = {nameList}")
    # 删除public.xml多余属性
    if nameList is not None and len(nameList) > len(attrNameList):
        for name in nameList:
            if name not in attrNameList:
                position = nameList.index(name)
                publicMappingNameData.get(fileType).pop(position)
                publicMappingChildData.get(fileType).pop(position)


# 删除public.xml注册标签
def deletePublicAttrName(attrName, fileType):
    nameList = publicMappingNameData.get(fileType)
    # 删除无用节点
    if nameList.count(attrName) > 0:
        pos = nameList.index(attrName)
        # print(f"attrName = {attrName} pos = {pos} fileType = {fileType}")
        publicMappingNameData.get(fileType).pop(pos)
        publicMappingChildData.get(fileType).pop(pos)


# 删除文件或xml属性集合
def deleteFileAndAttr(attrName, fileType):
    # 添加到删除属性json集合中
    if attrName not in deleteFileDict.get(fileType):
        deleteFileDict[fileType].append(attrName)


# 解析colors.xml、bools.xml等等xml
def parserColorXML(fpath, fileType):
    stringList = []
    parser = ET.parse(fpath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        text = child.text
        if attrName is None:
            continue
        # 是否允许添加该节点标签
        enableAdd = not text.__contains__(strPrefix)
        # print(f"attrName = {attrName} fpath = {fpath} fileType = {fileType}")
        if not attrName.startswith(strPrefix) and attrName in publicMappingNameData.get(fileType) and enableAdd:
            stringList.append(child)
            attrTypeDict.get(fileType).append(attrName)
        else:
            deletePublicAttrName(attrName, fileType)
            deleteFileAndAttr(attrName, fileType)
    # 重新写入xml文件
    xml_content = convert_str(stringList)
    saveXMLfile(xml_content, fpath)


# 解析string.xml、plurals.xml等等xml
def parserCommonXML(fpath, fileType):
    stringList = []
    parser = ET.parse(fpath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        if attrName is None:
            continue
        # print(f"attrName = {attrName} fpath = {fpath} fileType = {fileType}")
        if not attrName.startswith(strPrefix) and attrName in publicMappingNameData.get(fileType):
            stringList.append(child)
            attrTypeDict.get(fileType).append(attrName)
        else:
            deletePublicAttrName(attrName, fileType)
            deleteFileAndAttr(attrName, fileType)
    # 重新写入xml文件
    xml_content = convert_str(stringList)
    saveXMLfile(xml_content, fpath)


def convert_str(to_root):
    xml_content: str = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    sum = len(to_root)
    for index, child in enumerate(to_root):
        attr_tag = child.tag
        text = child.text
        xml_content += "    "
        # string标签中text内容">"会被转移为'&gt'
        if (attr_tag == "string" and str(text).__contains__(">")) or attr_tag == "plurals":
            child_str = ET.tostring(child, encoding="utf-8").decode('utf-8').strip().replace('&gt;', '>')
            xml_content += child_str
        else:
            xml_content += ET.tostring(child, encoding='utf-8').decode('utf-8').strip().replace('/>', ' />')
        if index < sum - 1:
            xml_content += '\n'

    xml_content += '\n</resources>\n'
    return xml_content


# 删除没有使用到的文件
def checkFile(from_dir):
    for attrType in fileList:
        if os.path.isdir(from_dir):
            if deleteFileDict.get(attrType) is None:
                deleteFileDict[attrType] = []
            transFolderFile(from_dir, publicMappingNameData.get(attrType), attrType)


def transFolderFile(from_dir, fileNameList, fileType):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath):
            transFolderFile(fpath, fileNameList, fileType)
        elif os.path.isfile(fpath):
            fileName = fname.split(".")[0]
            folderName = from_dir.split("/")[-1]
            if folderName.__contains__("-"):
                folderName = folderName.split("-")[0]
            if fileType == folderName:
                # print(f"folderName = {folderName} fileType = {fileType}")
                deleteFile(fileName, fpath, fileType, fileNameList)


def deleteFile(fileName, fpath, fileType, fileNameList):
    if fileName not in fileNameList:
        os.remove(fpath)
        deleteFileDict.get(fileType).append(fileName)
    else:
        attrTypeDict.get(fileType).append(fileName)


# 获取public.xml 属性id和属性name映射关系
def publicMapping(fpath, publicMappingChildData, publicMappingNameData):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = str(attrib.get("name"))
        attrType = attrib.get("type")
        attrId = attrib.get("id")
        if attrName is None or attrType is None or attrId is None:
            continue
        if attrName.startswith(strPrefix):
            continue
        # 映射child
        if publicMappingChildData.get(attrType) is None:
            publicMappingChildData[attrType] = []
        publicMappingChildData.get(attrType).append(child)
        # 映射name
        if publicMappingNameData.get(attrType) is None:
            publicMappingNameData[attrType] = []
        publicMappingNameData.get(attrType).append(attrName)


# 保存Json文件
def saveJsonFile(jsonData, fpath):
    jsonStr = json.dumps(jsonData, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，文件保存在:{fpath}")


# 保存XML文件
def saveXMLfile(data_str, target_file_path):
    try:
        with open(target_file_path, 'w+') as f:
            f.write(data_str)
        print(f"写入{target_file_path}")
    except Exception as result:
        print(f"写入{target_file_path}出现异常: {result}")


# 保存到public.xml
def save_to_publicXML(data_list, file_name):
    # print(file_name)
    with codecs.open(file_name, "w+", encoding="utf-8") as wf:
        wf.write('<?xml version="1.0" encoding="utf-8"?>\n')
        wf.write('<resources>\n')
        for typeName, childList in data_list.items():
            for child in childList:
                attr = child.attrib
                wf.write(f'    <public type="{attr["type"]}" name="{attr["name"]}" id="{attr["id"]}" />\n')
        wf.write('</resources>')


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.23.2.76_copy_diff"
    deleteGarbage(from_dir)
