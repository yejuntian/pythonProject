import codecs
import glob
import json
import os
import re
import xml.etree.ElementTree as ET
from scripts.insertcode.config import baseProjectPath, newProjectPath, baseVersionCode, newVersionCode
from scripts.insertcode.file_mapping import fileMapping

# 文件夹列表
folderList = ["smali", "smali_classes2", "smali_classes3", "smali_classes4", "smali_classes5"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF', 'original', 'apktool.yml',
             "smali_classes6", "smali_classes7", "smali_classes8", ]
# 只匹配下面的文件类型
extends = ["smali"]
# 映射文件集合
fileEntityList = []


# 根据fName查找文件
def findFileByName(fileName):
    fileList = []
    for folder in folderList:
        fileList.extend(glob.glob(f"{newProjectPath}/{folder}/**/{fileName}.smali", recursive=True))
    return fileList


# 通过字符串查找文件
def findXByStr(str):
    fileList = []
    fpath = f"{os.getcwd()}/classMapping.json"
    if len(fileEntityList) > 0:
        getFilePathList(str, fileList)
        return [os.path.join(newProjectPath, fpath) for fpath in fileList]
    else:
        if os.path.exists(fpath):
            getFileEntityList(fpath, str, fileList)
        else:
            fileMapping(baseProjectPath, newProjectPath)
            getFileEntityList(fpath, str, fileList)
    return [os.path.join(newProjectPath, fpath) for fpath in fileList]


def getFileEntityList(fpath, str, fileList):
    with open(fpath, encoding="utf-8") as rf:
        data = json.loads(rf.read())
        for item in data:
            oldClass = item[baseVersionCode]
            newClass = item[newVersionCode]
            string = item.get("string")
            id = item.get("id")
            entity = FileMappingEntity(oldClass, newClass, string, id)
            fileEntityList.append(entity)
            if str == string:
                fileList.append(newClass)
        # print(f"oldClass = {oldClass} newClass = {newClass} string = {string} id = {id}")


def getFilePathList(str, fileList):
    for entity in fileEntityList:
        if str == entity.string:
            return fileList.append(entity.newClazz)


# 遍历文件夹，把匹配到的文件路径添加到fileList集合中
def transFolder(from_dir, str, fileList):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        if fname not in blacklist:
            fpath = os.path.join(from_dir, fname)
            if os.path.isdir(fpath):
                transFolder(fpath, str, fileList)
            elif os.path.isfile(fpath):
                print(fpath)
                if fname.split(".")[-1] in extends:
                    data = getFileData(fpath)
                    if str in data or re.search(str, data):
                        fileList.append(fpath)


# 通过指定字符串比对，最终返回文件地址列表;allExcludeFileList：需要排除的类
# isRexMatch:False 通过字符串匹配,True:正则匹配
def getTransFileList(str, allExcludeFileList):
    if str is None:
        return []
    else:
        fileList = []
        newFileList = []
        allExcludeFileList = [os.path.join(newProjectPath, fpath) for fpath in allExcludeFileList]
        transFolder(newProjectPath, str, fileList)
        # 排除不需要替换的路径
        if allExcludeFileList is not None and len(allExcludeFileList) > 0:
            for fpath in fileList:
                if fpath not in allExcludeFileList:
                    newFileList.append(fpath)
            return newFileList
        else:
            return fileList


# 读取smali文件内容
def getFileData(codeFilePath):
    with codecs.open(codeFilePath, "r", "utf-8") as rf:
        return rf.read()


# 读取smali文件内容
def getFileLines(codeFilePath):
    with codecs.open(codeFilePath, "r", "utf-8") as rf:
        return rf.readlines()


# 读取smali文件内容
def getLines(filePath):
    with codecs.open(filePath, "r", "utf-8") as rf:
        return rf.readlines()


def getDefaultParam(match, lines, num, rowOffSet):
    if rowOffSet > 0:
        return lines[num + rowOffSet]
    else:
        return match.group(1)


# 获取指定param参数,（如果rowOffSet>0,则根据matchRex获取指定参数，否则根据regexList获取参数）
def getParam(str, regexList, func=None, rowOffSet=0, matchRex=None, isFindX=True):
    if isFindX:
        fileList = findXByStr(str)
    else:
        fileList = findFileByName(str)
    lines = getFileLines(fileList[0])
    data = "".join(lines)
    if func is None:
        # 单行正则匹配获取参数
        if is_1d_array(regexList) and fileList is not None and len(fileList) > 0:
            for num in range(0, len(lines)):
                matches = re.finditer(regexList[0], lines[num], re.MULTILINE)
                for match in matches:
                    param = getDefaultParam(match, lines, num, rowOffSet)
                    if param is not None:
                        # 根据regexList定位当前行，接着根据rowOffSet定位到目标行，最后根据matchRex正则匹配获取参数
                        if matchRex is not None:
                            # print(param)
                            matches = re.finditer(matchRex, param, re.MULTILINE)
                            for match in matches:
                                return match.group(1)
                        else:  # 根据regexList定位当前行，根据当前行中的正则获取参数
                            return param
        else:
            # 多行正则匹配获取参数
            for regex in regexList:
                matches = re.finditer(getMultilineRegex(regex), data, re.MULTILINE)
                for match in matches:
                    last_match_end = match.end()
                    num = data.count('\n', 0, last_match_end) - 1
                    param = getDefaultParam(match, lines, num, rowOffSet)
                    if param is not None:
                        return param
    else:
        matches = re.finditer(getMultilineRegex(regexList), getFileData(fileList[0]), re.MULTILINE)
        return func(matches, lines, 0, rowOffSet)


# 判断是否为一维数组
def is_1d_array(arr):
    return type(arr) == list and all(type(i) != list for i in arr)


class FileMappingEntity:
    def __init__(self, oldClazz, newClazz, string, id):
        self.oldClazz = oldClazz
        self.newClazz = newClazz
        self.string = string
        self.id = id


# 匹配多行正则
def getMultilineRegex(regexList):
    regexStr = ""
    for str in regexList:
        regexStr += (str + r"\n^\s*")
    return regexStr


# 获取上级目录
def getParentDirectory():
    return f"{os.getcwd().split('/insertcode')[0]}/insertcode"


# 获取public.xml资源id
def getPublicIdByName(attrName, attrType):
    res_dict = getMappingValues(f"{newProjectPath}/res/values/public.xml")
    return res_dict.get(f"{attrType}#{attrName}")


# 获取public资源ID和属性name、type的映射关系
def getMappingValues(fpath):
    res_dict = {}
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrType = attrib.get("type")
        attrId = attrib.get("id")
        if attrName is None or attrType is None or attrId is None:
            continue
        res_dict[f"{attrType.strip()}#{attrName.strip()}"] = attrId
    return res_dict
