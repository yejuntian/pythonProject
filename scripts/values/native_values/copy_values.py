import argparse
import codecs
import json
import os
import shutil
import traceback
import re
import lxml.etree as ET

# 需要插入的字典
enableInsertNameDict = {}
# 排除哪些文件夹
blacklist = ['.idea', '.git', '.gradle', 'build', 'kotlin', 'lib', 'META-INF',
             'original', 'AndroidManifest.xml', 'apktool.yml']
# 只匹配下面的文件类型
extends = ["xml"]
# 需要copy的type类型集合
typeList = ["array", "attr", "bool", "color", "dimen", "id",
            "integer", "string", "style", "anim", "drawable",
            "animator", "layout", "xml", "mipmap"]
# 不需要copy的文件类型，只需要在public.xml进行注册，copy操作单独进行处理
notCopyTypeList = ["anim", "drawable", "mipmap", "animator", "layout", "xml"]
# 文件名列表
fileNameList = ["arrays.xml", "attrs.xml", "bools.xml", "colors.xml",
                "dimens.xml", "ids.xml", "integers.xml", "strings.xml",
                "styles.xml"]
# 需要copy的映射关系
copy_dict = {}
# 需要copy的属性name字典
diffNameDict = {}

# 文件拷贝，只匹配下面的文件类型
reSExtends = ["png", "xml", "jpg"]
resTypeList = ["animator", "color", "drawable", "mipmap", "layout", "anim", "xml"]
# 是否重命名style名称
isRenameStyle = True
"""
    主要作用：根据GBNeedToFind.json 复制对应类型的属性到目标项目中。
"""


def startCopyValues(from_dir, to_dir):
    mappingData = getNameMappingList("scripts/values/native_values/GBNeedToFind.json")
    publicFilePath = os.path.join(to_dir, "res/values/public.xml")
    getInsertNameList(publicFilePath, typeList, mappingData)
    travelFolderCopyAttr(from_dir, to_dir)
    for type in typeList:
        # 特殊处理，只需要注册到public.xml，copy操作单独处理
        if type in notCopyTypeList:
            enableInsertNameDict[type] = getInsertName(publicFilePath, type, mappingData.get(type))
        insertPublic(publicFilePath, type)

    # 执行拷贝资源操作
    copyRes(from_dir, to_dir, mappingData)
    print(f"程序执行结束，结果保存在{to_dir}")


def copyRes(from_dir, to_dir, mappingData):
    resMappingData = {}
    for key, value in mappingData.items():
        if key in resTypeList and len(value) > 0:
            resMappingData[key] = value
    # 有需要copy的资源类型才进行遍历
    if len(resMappingData) > 0:
        print("***************正在执行拷贝资源操作****************")
        transFolderCopy(from_dir, to_dir, resMappingData)


# 遍历整个项目复制资源文件到目标项目
def transFolderCopy(from_dir, to_dir, mappingData):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        tpath = os.path.join(to_dir, fname)
        if os.path.isdir(fpath):
            transFolderCopy(fpath, tpath, mappingData)
        elif os.path.isfile(fpath):
            if fname.split(".")[-1] in reSExtends:
                fileName = fname.split(".")[0]
                folderName = fpath.split("/")[-2]
                # 目标文件夹列表
                parentFolderPath = os.path.dirname(tpath)
                if not os.path.exists(parentFolderPath):
                    os.makedirs(parentFolderPath, exist_ok=True)
                folderList = os.listdir(parentFolderPath)
                if folderName.__contains__("-"):
                    folderName = folderName.split("-")[0]
                if folderName == "mipmap" or folderName == "drawable":
                    drawableList = mappingData.get(folderName)
                    # 在copy列表中，并且目标文件夹不存在则进行copy操作
                    if drawableList is not None and fileName in drawableList and fname not in folderList:
                        shutil.copy(fpath, tpath)
                elif folderName in resTypeList:
                    otherFileList = mappingData.get(folderName)
                    # 在copy列表中，并且目标文件夹不存在则进行copy操作
                    # print(f"folderName = {folderName} fileName = {fileName}")
                    # print(otherFileList)
                    if otherFileList is not None and fileName in otherFileList and fname not in folderList:
                        shutil.copy(fpath, tpath)


def getNameMappingList(fpath):
    dict = {}
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = json.loads(rf.read())
        for attrType, nameList in data.items():
            if dict.get(attrType) is None:
                dict[attrType] = []
            for name in nameList:
                # 特殊处理
                if attrType == "style" and isRenameStyle:
                    name = name.replace("_", ".")
                # 去重操作
                if not name in dict[attrType]:
                    dict[attrType].append(name)
    return dict


# 对比public.xml，把没有注册的属性添加到集合中
def getInsertName(targetPath, fileType, diffNameList):
    if enableInsertNameDict.get(fileType) is None:
        enableInsertNameDict[fileType] = []
    if diffNameList is None or len(diffNameList) <= 0:
        return
    targetNameList = getTargetTypePublicId(targetPath, fileType)
    for diffName in diffNameList:
        # 去重
        if not diffName in targetNameList and not diffName in enableInsertNameDict[fileType]:
            enableInsertNameDict[fileType].append(diffName)
    return enableInsertNameDict[fileType]


def getInsertNameList(fpath, typeList, mappingData):
    parser = ET.parse(fpath)
    root = parser.getroot()
    attrNameDict = {}
    for child in root:
        child_attr = child.attrib
        attr_name = child_attr.get("name")
        attr_type = child_attr.get("type")
        if not attr_name is None and not attr_type is None and attr_type in typeList:
            namelist = attrNameDict.get(attr_type)
            if namelist is None:
                attrNameDict[attr_type] = []
            attrNameDict[attr_type].append(attr_name)

    for attrType, attrNameList in mappingData.items():
        stringList = attrNameDict.get(attrType)
        # print(attrType)
        # print(attrNameList)
        if stringList is None or len(stringList) <= 0:
            continue
        for attrName in attrNameList:
            if not attrName in stringList:
                if diffNameDict.get(attrType) is None:
                    diffNameDict[attrType] = []
                diffNameDict[attrType].append(attrName)
    # print(diffNameDict)


def travelFolderCopyAttr(from_dir, to_dir):
    from_listdir = os.listdir(from_dir)
    to_listdir = os.listdir(to_dir)
    for fname in from_listdir:
        if not fname in blacklist:
            fpath = os.path.join(from_dir, fname)
            tpath = os.path.join(to_dir, fname)
            if os.path.isdir(fpath):
                # 不在目标目录，创建新文件夹
                if not fname in to_listdir:
                    os.makedirs(tpath, exist_ok=True)
                travelFolderCopyAttr(fpath, tpath)
            elif os.path.isfile(fpath):
                if fname.split(".")[-1] in extends and fname in fileNameList:
                    print(tpath)
                    startCopyAttr(fpath, tpath, fname.split(".")[0])


def startCopyAttr(fpath, tpath, fname):
    fileType = fname[0:len(fname) - 1]
    # 目标文件不存在
    if not os.path.exists(tpath):
        createNewFile(fpath, tpath, fileType)
    else:
        insertExitFile(fpath, tpath, fileType)


# 创建新文件插入diff code
def createNewFile(fpath, tpath, fileType):
    diffNameList = diffNameDict.get(fileType)
    if diffNameList is None or len(diffNameList) <= 0:
        return
    from_parser = ET.parse(fpath)
    from_root = from_parser.getroot()
    fromNameList = []
    isChanged: bool = False
    for fromChild in from_root:
        from_attr = fromChild.attrib
        from_attr_name = from_attr.get("name")
        if not from_attr_name is None and from_attr_name in diffNameList:
            isChanged = True
            fromNameList.append(fromChild)
            if enableInsertNameDict.get(fileType) is None:
                enableInsertNameDict[fileType] = []
            if not from_attr_name in enableInsertNameDict.get(fileType):
                enableInsertNameDict[fileType].append(from_attr_name)
    if isChanged:
        xml_content = convert_str(fromNameList)
        save_2_file(xml_content, tpath)


# 特殊处理类型如dimen
def specialLogic(diffNameList, oldStr, newStr):
    if diffNameList is None:
        return diffNameList
    newNameList = []
    regex = r"(.*common_dimens_)(\d+[_.]\d+dp)"
    for name in diffNameList:
        matches = re.finditer(regex, name, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            preName = match.group(1)
            lastName = match.group(2)
            # print(f"preName = {preName} lastName = {lastName}")
            name = f"{preName}{lastName.replace(oldStr, newStr)}"
        newNameList.append(name)
    return newNameList


# diff code插入到已存在的文件
def insertExitFile(fpath, tpath, fileType):
    diffNameList = diffNameDict.get(fileType)
    # 对dimen这种类型特殊处理
    if fileType == "dimen":
        diffNameList = specialLogic(diffNameList, '_', '.')
        diffNameDict[fileType] = diffNameList

    if diffNameList is None or len(diffNameList) <= 0:
        return
    to_parser = ET.parse(tpath)
    to_root = to_parser.getroot()
    toNameList = []
    for toChild in to_root:
        to_attr = toChild.attrib
        to_attr_name = to_attr.get("name")
        if not to_attr_name is None:
            toNameList.append(to_attr_name)

    from_parser = ET.parse(fpath)
    from_root = from_parser.getroot()
    isChanged: bool = False
    for fromChild in from_root:
        from_attr = fromChild.attrib
        from_attr_name = from_attr.get("name")
        if not from_attr_name is None and not from_attr_name in toNameList and from_attr_name in diffNameList:
            isChanged = True
            to_root.append(fromChild)
            if enableInsertNameDict.get(fileType) is None:
                enableInsertNameDict[fileType] = []
            if not from_attr_name in enableInsertNameDict.get(fileType):
                enableInsertNameDict[fileType].append(from_attr_name)
    if isChanged:
        xml_content = convert_str(to_root)
        # 合并其他string.xml
        save_2_file(xml_content, tpath)
    addInsertNameList(tpath, fileType, diffNameList)


# 对比public.xml，把没有注册的属性添加到集合中
def addInsertNameList(tpath, fileType, diffNameList):
    targetPath = tpath[0:tpath.index("/res/values")]
    targetNameList = getTargetTypePublicId(f"{targetPath}/res/values/public.xml", fileType)
    for name in diffNameList:
        if not name in targetNameList:
            if enableInsertNameDict.get(fileType) is None:
                enableInsertNameDict[fileType] = []
            if name not in enableInsertNameDict[fileType]:
                enableInsertNameDict[fileType].append(name)
    # print(enableInsertNameDict[fileType])


# 在public.xml中获取指定类型的name集合
def getTargetTypePublicId(fpath, targetType):
    targetNameList = []
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        name = attrib.get("name")
        type = attrib.get("type")
        if not name is None and not type is None and type == targetType:
            targetNameList.append(name)
    return targetNameList


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


def insertPublic(fpath, type):
    to_parser = ET.parse(fpath)
    to_root = to_parser.getroot()
    maxChild = None
    maxId = 0
    for child in to_root:
        attr = child.attrib
        attrType = attr.get("type")
        attrId = attr.get("id")
        if not attrType is None and attrType == type:
            attrId = int(attrId, 16)
            if attrId >= maxId:
                maxId = attrId
                maxChild = child

    pos = to_root.index(maxChild)
    enableInsertNameList = enableInsertNameDict.get(type)
    if enableInsertNameList is None or len(enableInsertNameList) <= 0:
        return
    # 对dimen这种类型特殊处理
    # if type == "dimen":
    #     enableInsertNameList = specialLogic(enableInsertNameList, '.', '_')
    for itemName in enableInsertNameList:
        maxId += 1
        pos += 1

        element = ET.SubElement(to_root, "public")
        element.set("type", type)
        element.set("name", itemName)
        element.set("id", str(hex(maxId)))
        to_root.insert(pos, element)

    # 写入到public.xml文件中
    with codecs.open(fpath, "w+", encoding="utf-8") as wf:
        wf.write('<?xml version="1.0" encoding="utf-8"?>\n')
        wf.write('<resources>\n')
        for child in to_root:
            attrType = child.attrib.get("type")
            attrName = child.attrib.get("name")
            attrId = child.attrib.get("id")
            wf.write(f'    <public type="{attrType}" name="{attrName}" id="{attrId}" />\n')
        wf.write('</resources>')


if __name__ == "__main__":
    # from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    # to_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.22.24.78"
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    args = parser.parse_args()
    startCopyValues(args.from_dir, args.to_dir)
