import argparse
import codecs
import glob
import json
import os
import re
import xml.etree.ElementTree as ET

# 匹配字符串
regexStr = r"\"(.*)\""
# 匹配16进制id
regexId = r"(0x7f\w{6})"
baseVersionCode = "2.22.10.73"
newVersionCode = "2.23.2.76"

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
    fromIdMapping = getIdMapping(getFileMapping(from_dir, regexId), from_dir)

    toStrMapping = getFileMapping(to_dir, regexStr)
    toIdMapping = getIdMapping(getFileMapping(to_dir, regexId), to_dir)
    entityList = getEntityList(fromStrMapping, fromIdMapping, toStrMapping, toIdMapping)
    print("------映射完对应关系，开始保存到classMapping.json文件中------")
    save2File(f"{os.getcwd()}/scripts/findX/file_mapping", entityList, "classMapping.json")


def save2File(folder_path, dataList, fileName):
    newList = []
    for entity in dataList:
        tempDict = {}
        tempDict[baseVersionCode] = entity.oldClazz
        tempDict[newVersionCode] = entity.newClazz
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
def getEntityList(fromStrMapping, fromIdMapping, toStrMapping, toIdMapping):
    dict = {}
    # 根据字符串映射class
    for fromStr, fromValue in fromStrMapping.items():
        oldClass = getClassName(fromValue)
        toClass = getClassName(toStrMapping.get(fromStr))
        if not toClass is None:
            entity = FileMappingEntity(oldClass, None, None, fromStr, None, toClass)
            dict[oldClass] = entity
    # 根据ID映射class
    for clazz, name in fromIdMapping.items():
        oldClass = getClassName(clazz)
        toClass = getClassName(toIdMapping.get(name))
        if not oldClass in dict and not toClass is None:
            entity = FileMappingEntity(oldClass, None, None, None, name, toClass)
            dict[oldClass] = entity
        else:
            entity = dict.get(oldClass)
            if not entity is None:
                entity.id = name
                dict[oldClass] = entity
    return dict.values()


def getClassName(fpath):
    if not fpath is None:
        baseName = os.path.basename(fpath)
        pos = baseName.index(".")
        return f"LX/{baseName[:pos]};"
    else:
        return None


def getIdMapping(idMapping, from_dir):
    publicIdMapping = getPublicMapping(f"{from_dir}/res/values/public.xml")
    dict = {}
    for key, value in idMapping.items():
        key = publicIdMapping.get(key)
        dict[value] = key
    return dict


# 获取public.xml对应关系
def getPublicMapping(fpath):
    parser = ET.parse(fpath)
    root = parser.getroot()
    dict = {}
    for child in root:
        attrib = child.attrib
        id = attrib.get("id")
        name = attrib.get("name")
        dict[id] = name
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    to_dir = args.to_dir
    # from_dir = "/Users/shareit/work/shareit/wa_diff_gb/wa_diff_gbv17"
    # to_dir = "/Users/shareit/work/GBWorke/whatsapp_new/Whatsapp_v2.23.2.76"
    fileMapping(from_dir, to_dir)
