import argparse
import codecs
import glob
import json
import os
import re
import shutil
import lxml.etree as ET
import traceback

# 需要插入的字典
enableInsertNameDict = {}
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF', 'original', 'smali',
             'smali_classes2', 'smali_classes3', 'smali_classes4', 'smali_classes5',
             'smali_classes6', 'smali_classes7', 'smali_classes8', 'smali_classes9',
             'smali_classes10', 'smali_classes11', 'gen', 'AndroidManifest.xml', 'apktool.yml']

# 只匹配下面的文件类型
extends = ["xml"]
# 需要特殊处理的type
extendsType = ["plural"]
# 需要copy的type类型集合
typeList = ["array", "attr", "bool", "color", "dimen", "id",
            "integer", "string", "style", "plurals", "fraction"]
# 文件名列表
fileNameList = ["arrays.xml", "attrs.xml", "bools.xml", "colors.xml",
                "dimens.xml", "ids.xml", "integers.xml", "strings.xml",
                "styles.xml", "plurals.xml", "fractions.xml"]
# 需要copy的映射关系
copy_dict = {}
# 需要copy的属性name字典
diffNameDict = {}

# 文件拷贝，只匹配下面的文件类型
reSExtends = ["png", "xml", "jpg", "webp", "ttf"]
resTypeList = ["color", "anim", "drawable", "mipmap", "animator",
               "layout", "xml", "interpolator", "menu", "transition",
               "font"]
# 需要注册的资源集合
insertResDict = {}
# *******************用于校验注入的属性****************************
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
"""
    主要作用：根据GBNeedToFind.json 复制对应类型的属性到目标项目中。
"""


def startCopyValues(from_dir, to_dir):
    getCheckAttrDic(f"{from_dir}/res")
    jsonPath = "scripts/values/native_values/GBNeedToFind.json"
    mappingData = getNameMappingList(jsonPath)
    publicFilePath = os.path.join(to_dir, "res/values/public.xml")
    publicDict = parserPublicXML(publicFilePath)
    getInsertNameList(publicDict, mappingData)
    travelFolderCopyAttr(from_dir, to_dir)
    for attrType in typeList:
        insertPublic(publicFilePath, attrType, publicDict)
    # 执行拷贝资源操作
    copyRes(from_dir, to_dir, mappingData, publicFilePath, publicDict)
    print(f"程序执行结束，结果保存在{to_dir}")
    print("*****************不存在的属性名称如下*****************")
    save_2_file(json.dumps(notFindAttrDict, ensure_ascii=False, indent=2), f"{os.getcwd()}/{jsonPath}")
    print(notFindAttrDict)


def copyRes(from_dir, to_dir, mappingData, publicFilePath, publicDict):
    resMappingData = {}
    for resType, nameList in mappingData.items():
        if resType in resTypeList and len(nameList) > 0:
            resMappingData[resType] = nameList
    # 有需要copy的资源类型才进行遍历
    if len(resMappingData) > 0:
        print("***************正在执行拷贝资源操作****************")
        transFolderCopy(from_dir, to_dir, resMappingData, insertResDict, publicDict)
        for attrType, resNameList in insertResDict.items():
            insertResPublic(publicFilePath, attrType, resNameList, publicDict)
        # 添加没有copy的res资源属性
        for attrType, resNameList in resMappingData.items():
            publicNameList = publicDict.get(attrType)
            if notFindAttrDict.get(attrType) is None:
                notFindAttrDict[attrType] = []
            for resName in resNameList:
                if resName not in publicNameList and resName not in notFindAttrDict.get(attrType):
                    notFindAttrDict[attrType].append(resName)


# 遍历整个项目复制资源文件到目标项目
def transFolderCopy(from_dir, to_dir, resMappingData, insertResDict, publicDict):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        if fname not in blacklist:
            fpath = os.path.join(from_dir, fname)
            tpath = os.path.join(to_dir, fname)
            if os.path.isdir(fpath):
                transFolderCopy(fpath, tpath, resMappingData, insertResDict, publicDict)
            elif os.path.isfile(fpath):
                if fname.split(".")[-1] in reSExtends:
                    fileName = fname.split(".")[0]
                    folderName = fpath.split("/")[-2]
                    # 目标文件夹列表
                    parentFolderPath = os.path.dirname(tpath)
                    if not os.path.exists(parentFolderPath):
                        os.makedirs(parentFolderPath, exist_ok=True)
                    targetFolderList = os.listdir(parentFolderPath)
                    if folderName.__contains__("-"):
                        folderName = folderName.split("-")[0]
                    if folderName in resTypeList:
                        fileList = resMappingData.get(folderName)
                        # 在copy列表中，并且目标文件夹不存在该文件，则进行copy操作
                        if fileList is not None and fileName in fileList and fname not in targetFolderList:
                            # print(f"folderName = {folderName} fileName = {fileName}")
                            shutil.copy(fpath, tpath)
                            # 添加到注册public.xml集合中
                            if insertResDict.get(folderName) is None:
                                insertResDict[folderName] = []
                            if fileName not in insertResDict.get(folderName) and fileName not in publicDict.get(folderName):
                                insertResDict[folderName].append(fileName)
                                # 删除未发现的属性
                                notFoundList = notFindAttrDict.get(folderName)
                                if notFoundList is not None and fileName in notFoundList:
                                    # print(f"remove fileName = {fileName}")
                                    notFindAttrDict.get(folderName).pop()


# 获取需要copy的数据列表集合
def getNameMappingList(fpath):
    temDict = {}
    styleType = spacialTypeList[0]
    styleNameList = checkAttrDict.get(styleType)
    dimenNameList = checkAttrDict.get(spacialTypeList[1])

    if notFindAttrDict.get(styleType) is None:
        notFindAttrDict[styleType] = []
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = json.loads(rf.read())
        for attrType, nameList in data.items():
            if temDict.get(attrType) is None:
                temDict[attrType] = []
            for attrName in nameList:
                # 特殊处理
                attrNameTuple = getSpecialTypeName(attrType, attrName, styleNameList,
                                                   dimenNameList)
                if attrNameTuple[1]:
                    continue
                attrName = attrNameTuple[0]
                # 去重操作
                if not attrName.startswith("APKTOOL_DUMMYVAL_0x7f") and attrName not in temDict[attrType]:
                    temDict[attrType].append(attrName)
    return temDict


# style/dimen样式需要特殊处理
def getSpecialTypeName(fileType, attrName, styleNameList, dimenNameList):
    # 是否过滤该属性
    enableContinue = False
    if fileType == "style":
        if attrName.replace("_", ".") in styleNameList:
            attrName = attrName.replace("_", ".")
        elif attrName.replace(".", "_") in styleNameList:
            attrName = attrName.replace(".", "_")
        else:
            enableContinue = True
            if attrName not in notFindAttrDict[fileType]:
                notFindAttrDict[fileType].append(attrName)
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
    return attrName, enableContinue


def parserPublicXML(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    # 用户存放public.xml所有属性集合
    attrNameDict = {}
    for child in root:
        child_attr = child.attrib
        attr_name = child_attr.get("name")
        attr_type = child_attr.get("type")
        if attr_name is not None and attr_type is not None:
            if attrNameDict.get(attr_type) is None:
                attrNameDict[attr_type] = []
            attrNameDict[attr_type].append(attr_name)
    return attrNameDict


def getInsertNameList(publicDict, mappingData):
    for attrType, attrNameList in mappingData.items():
        publicAttrNameList = publicDict.get(attrType)
        if publicAttrNameList is None or len(publicAttrNameList) <= 0:
            continue
        for attrName in attrNameList:
            if attrName not in publicAttrNameList:
                if diffNameDict.get(attrType) is None:
                    diffNameDict[attrType] = []
                diffNameDict[attrType].append(attrName)
    # print(diffNameDict)


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


def travelFolderCopyAttr(from_dir, to_dir):
    from_listdir = os.listdir(from_dir)
    to_listdir = os.listdir(to_dir)
    for fname in from_listdir:
        if fname not in blacklist:
            fpath = os.path.join(from_dir, fname)
            tpath = os.path.join(to_dir, fname)
            if os.path.isdir(fpath):
                # 不在目标目录，创建新文件夹
                if fname not in to_listdir:
                    os.makedirs(tpath, exist_ok=True)
                travelFolderCopyAttr(fpath, tpath)
            elif os.path.isfile(fpath):
                if fname.split(".")[-1] in extends and fname in fileNameList:
                    print(tpath)
                    startCopyAttr(fpath, tpath, fname.split(".")[0])


def startCopyAttr(fpath, tpath, fname):
    fileType = fname[0:len(fname) - 1]
    if fileType in extendsType:
        fileType = f"{fileType}s"
    # 目标文件不存在
    if not os.path.exists(tpath):
        createNewFile(fpath, tpath, fileType)
    else:
        insertExitFile(fpath, tpath, fileType)


# 创建新文件插入diff code
def createNewFile(fpath, tPath, fileType):
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
        if from_attr_name is not None and from_attr_name in diffNameList:
            isChanged = True
            fromNameList.append(fromChild)
            if enableInsertNameDict.get(fileType) is None:
                enableInsertNameDict[fileType] = []
            if from_attr_name not in enableInsertNameDict.get(fileType):
                enableInsertNameDict[fileType].append(from_attr_name)
    if isChanged:
        xml_content = convert_str(fromNameList)
        save_2_file(xml_content.replace('&gt;', '>'), tPath)


# diff code插入到已存在的文件
def insertExitFile(fpath, tPath, fileType):
    diffNameList = diffNameDict.get(fileType)
    if diffNameList is None or len(diffNameList) <= 0:
        return
    to_parser = ET.parse(tPath)
    to_root = to_parser.getroot()
    toNameList = []
    for toChild in to_root:
        to_attr = toChild.attrib
        to_attr_name = to_attr.get("name")
        if to_attr_name is not None:
            toNameList.append(to_attr_name)

    from_parser = ET.parse(fpath)
    from_root = from_parser.getroot()
    isChanged: bool = False
    for fromChild in from_root:
        from_attr = fromChild.attrib
        from_attr_name = from_attr.get("name")
        if from_attr_name is not None and from_attr_name not in toNameList and from_attr_name in diffNameList:
            isChanged = True
            to_root.append(fromChild)
            if enableInsertNameDict.get(fileType) is None:
                enableInsertNameDict[fileType] = []
            if from_attr_name not in enableInsertNameDict.get(fileType):
                enableInsertNameDict[fileType].append(from_attr_name)
    if isChanged:
        xml_content = convert_str(to_root)
        # 合并其他string.xml
        save_2_file(xml_content.replace('&gt;', '>'), tPath)
    addInsertNameList(tPath, fileType, diffNameList)


# 对比public.xml，把没有注册的属性添加到集合中
def addInsertNameList(tpath, fileType, diffNameList):
    targetPath = tpath[0:tpath.index("/res/values")]
    targetNameList = getTargetTypePublicId(f"{targetPath}/res/values/public.xml", fileType)
    for name in diffNameList:
        if name not in targetNameList:
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
        attType = attrib.get("type")
        if name is not None and attType is not None and attType == targetType:
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


def insertPublic(fpath, type, publicDict):
    to_parser = ET.parse(fpath)
    to_root = to_parser.getroot()
    maxChild = None
    maxId = 0
    for child in to_root:
        attr = child.attrib
        attrType = attr.get("type")
        attrId = attr.get("id")
        if attrType is not None and attrType == type:
            attrId = int(attrId, 16)
            if attrId >= maxId:
                maxId = attrId
                maxChild = child

    pos = to_root.index(maxChild)
    enableInsertNameList = enableInsertNameDict.get(type)
    checkTypeList = checkAttrDict.get(type)
    if enableInsertNameList is None or len(enableInsertNameList) <= 0:
        return

    for itemName in enableInsertNameList:
        # 过滤掉不存在的属性名的注册
        if isFilterRegisterAttrName(itemName, type, checkTypeList):
            continue
        maxId += 1
        pos += 1

        element = ET.SubElement(to_root, "public")
        element.set("type", type)
        element.set("name", itemName)
        element.set("id", str(hex(maxId)))
        to_root.insert(pos, element)
        publicDict[type].append(itemName)

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


def insertResPublic(fpath, resType, resNameList, publicDict):
    if resNameList is None or len(resNameList) < 0:
        return
    to_parser = ET.parse(fpath)
    to_root = to_parser.getroot()
    maxChild = None
    maxId = 0
    for child in to_root:
        attr = child.attrib
        attrType = attr.get("type")
        attrId = attr.get("id")
        if attrType is not None and attrType == resType:
            attrId = int(attrId, 16)
            if attrId >= maxId:
                maxId = attrId
                maxChild = child

    pos = to_root.index(maxChild)
    for itemName in resNameList:
        maxId += 1
        pos += 1

        element = ET.SubElement(to_root, "public")
        element.set("type", resType)
        element.set("name", itemName)
        element.set("id", str(hex(maxId)))
        to_root.insert(pos, element)
        publicDict[resType].append(itemName)

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


# 过滤掉不存在的属性名称，取消public.xml的注册操作
def isFilterRegisterAttrName(itemName, type, checkTypeList):
    if checkTypeList is None:
        return False
    else:
        if itemName not in checkTypeList:
            if itemName not in notFindAttrDict[type]:
                notFindAttrDict[type].append(itemName)
            return True
        else:
            return False


if __name__ == "__main__":
    # from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    # to_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.22.24.78"
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    args = parser.parse_args()
    startCopyValues(args.from_dir, args.to_dir)
