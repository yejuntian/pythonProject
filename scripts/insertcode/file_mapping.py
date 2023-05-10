import codecs
import glob
import json
import os
import re
import xml.etree.ElementTree as ET
from scripts.insertcode.config import baseVersionCode, newVersionCode

# 匹配字符串
regexStr = r"\"(.*)\""
# 匹配16进制id
regexId = r"(0x7f\w{6})"
targetPublicIdDict = {}

"""
    主要作用：根据from_dir、to_dir项目路径，获取X包下对应关系，
    并保存到scripts/findX/file_mapping/classMapping.json
"""


class FileMappingEntity():
    def __init__(self, oldClazz, reference, method, string, id, newClazz):
        self.oldClazz = oldClazz
        self.reference = reference
        self.method = method
        self.string = string
        self.id = id
        self.newClazz = newClazz


def fileMapping(from_dir, to_dir):
    fromStrMapping = getFileMapping(from_dir, regexStr)
    fromIdMapping = getIdMapping(getFileMapping(from_dir, regexId), from_dir, False)

    toStrMapping = getFileMapping(to_dir, regexStr)
    toIdMapping = getIdMapping(getFileMapping(to_dir, regexId), to_dir, True)
    entityList = getEntityList(from_dir, to_dir, fromStrMapping, fromIdMapping, toStrMapping, toIdMapping)
    print("------映射完对应关系，开始保存到classMapping.json文件中------")
    # save2File(f"{os.getcwd()}/scripts/findX/file_mapping", entityList, "classMapping.json")
    save2File(f"{os.getcwd()}", entityList, "classMapping.json")


def save2File(folder_path, dataList, fileName):
    newList = []
    for entity in dataList:
        tempDict = {baseVersionCode: entity.oldClazz, newVersionCode: entity.newClazz}
        if not entity.string is None:
            tempDict["string"] = entity.string
        if not entity.id is None:
            tempDict["id"] = entity.id
        newList.append(tempDict)
    jsonStr = json.dumps(newList, ensure_ascii=False, indent=2)
    savePath = os.path.join(folder_path, fileName)
    with codecs.open(savePath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"结果保存到：{savePath}")


# 获取entity对应关系
def getEntityList(from_dir, to_dir, fromStrMapping, fromIdMapping, toStrMapping, toIdMapping):
    dict = {}
    # 根据字符串映射class
    for fromStr, fromValue in fromStrMapping.items():
        oldClass = getClassName(from_dir, fromValue)
        toClass = getClassName(to_dir, toStrMapping.get(fromStr))
        if not toClass is None:
            entity = FileMappingEntity(oldClass, None, None, fromStr, None, toClass)
            dict[oldClass] = entity
    # 根据ID映射class
    for attrName, clazz in fromIdMapping.items():
        oldClass = getClassName(from_dir, clazz)
        toClass = getClassName(to_dir, toIdMapping.get(attrName))
        if toClass is None or (not attrName is None and attrName.__contains__("APKTOOL_DUMMYVAL_")):
            continue
        if not oldClass in dict:
            id = targetPublicIdDict.get(attrName)
            entity = FileMappingEntity(oldClass, None, None, None, f"{attrName}#{id}", toClass)
            dict[oldClass] = entity
        else:
            entity = dict.get(oldClass)
            if not entity is None:
                entity.id = f"{attrName}#{targetPublicIdDict.get(attrName)}"
                dict[oldClass] = entity
    return dict.values()


def getClassName(from_dir, fpath):
    if not fpath is None:
        return fpath[len(from_dir) + 1:]
    else:
        return None


# 获取属性和文件路径对应关系 （eg:key = 'APKTOOL_DUMMYVAL_0x7f120cd4#string'   value = "文件路径"）
def getIdMapping(idMapping, from_dir, isTargetProject):
    stringMapping = getStringMapping(f"{from_dir}/res/values/strings.xml")
    fpath = f"{from_dir}/res/values/public.xml"
    publicIdMapping = getPublicMapping(fpath, stringMapping, isTargetProject)
    dict = {}
    for key, value in idMapping.items():
        key = publicIdMapping.get(key)
        dict[key] = value

    return dict


# 获取string.xml name和text映射关系
def getStringMapping(fpath):
    parser = ET.parse(fpath)
    root = parser.getroot()
    dict = {}
    for child in root:
        text = child.text
        name = child.attrib.get("name")
        if not text is None and not name is None:
            dict[name] = text
    return dict


# 获取public.xml对应关系
def getPublicMapping(fpath, stringMapping, isTargetProject):
    parser = ET.parse(fpath)
    root = parser.getroot()
    dict = {}
    for child in root:
        attrib = child.attrib
        id = attrib.get("id")
        name = attrib.get("name")
        type = attrib.get("type")
        if not name is None and not id is None:
            if name.startswith("APKTOOL_DUMMYVAL_") and type == "string":
                name = stringMapping.get(name)
            value = f"{name}#{type}"
            if not value in dict.values():
                dict[id] = value
                # 保存属性和Id映射关系
                if isTargetProject:
                    targetPublicIdDict[value] = id
    return dict


# 获取文件的映射关系
def getFileMapping(from_dir, regex):
    dict = {}
    # 获取X目录下所有文件
    filePathList = glob.glob(from_dir + "/smali*/X/*.smali", recursive=True)
    for fpath in filePathList:
        with codecs.open(fpath, "r", 'utf-8') as rf:
            data = rf.read()
            matches = re.finditer(regex, data, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                item = match.group(1)
                if item not in dict:
                    dict[item] = set()
                dict[item].add(fpath)
    filterDict = {k: v for k, v in dict.items() if len(v) == 1}
    new_dict = {}
    for key, value in filterDict.items():
        new_dict[key] = list(value)[0]
    return new_dict
