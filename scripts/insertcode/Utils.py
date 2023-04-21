import codecs
import glob
import json
import os
import re
from config import baseProjectPath, newProjectPath, baseVersionCode, newVersionCode
from file_mapping import fileMapping

# 文件夹列表
folderList = ["smali", "smali_classes2", "smali_classes3", "smali_classes4"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF', 'original', 'apktool.yml',
             "smali_classes5", "smali_classes6", "smali_classes7", "smali_classes8", ]
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
        return fileList
    else:
        if os.path.exists(fpath):
            getFileEntityList(fpath, str, fileList)
        else:
            fileMapping(baseProjectPath, newProjectPath)
            getFileEntityList(fpath, str, fileList)
    return fileList


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
                    if str in getFileData(fpath):
                        fileList.append(fpath)


# 通过指定字符串比对，最终返回文件地址列表
def getTransFileList(str):
    fileList = []
    transFolder(newProjectPath, str, fileList)
    return fileList


# 读取smali文件内容
def getFileData(codeFilePath):
    with codecs.open(codeFilePath, "r", "utf-8") as rf:
        return rf.read()


# 读取smali文件内容
def getLines(filePath):
    with codecs.open(filePath, "r", "utf-8") as rf:
        return rf.readlines()


def getDefaultParam(matches):
    for match in matches:
        return match.group(1)


# 获取指定param参数
def getParam(str, regexList, func=None):
    fileList = findXByStr(str)
    if func is None:
        if fileList is not None and len(fileList) > 0:
            return getDefaultParam(re.finditer(getMultilineRegex(regexList), getFileData(fileList[0]), re.MULTILINE))
    else:
        return func(re.finditer(getMultilineRegex(regexList), getFileData(fileList[0]), re.MULTILINE))


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
