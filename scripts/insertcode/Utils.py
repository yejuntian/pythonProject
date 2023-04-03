import codecs
import glob
import os

projectPath = "/Users/shareit/work/GBWorke/whatsapp_new/Whatsapp_v2.23.2.76"
# 文件夹列表
folderList = ["smali", "smali_classes2", "smali_classes3", "smali_classes4"]
# 只匹配下面的文件类型
extends = ["smali"]


# 根据fName查找文件
def findFileByName(fileName):
    fileList = []
    for folder in folderList:
        fileList.extend(glob.glob(f"{projectPath}/{folder}/**/{fileName}.smali", recursive=True))
    return fileList


# 通过字符串查找文件
def findFileByStr(str):
    fileList = []
    transFolder(projectPath, str, fileList)
    return fileList


# 遍历文件夹，把匹配到的文件路径添加到fileList集合中
def transFolder(from_dir, str, fileList):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        if fname in folderList:
            fpath = os.path.join(from_dir, fname)
            if os.path.isdir(fpath):
                transFolder(fpath, str, fileList)
            elif os.path.isfile(fpath):
                if fname.split(".")[-1] in extends:
                    if str in getSmaliCode(fpath):
                        fileList.append(fpath)


# 读取smali文件内容
def getSmaliCode(codeFilePath):
    with codecs.open(codeFilePath, "r", "utf-8") as rf:
        return rf.read()
