import glob
import os
import shutil
import json
import codecs
import xml.etree.ElementTree as ET

checkTypeList = ["anim", "animator", "drawable", "font", "interpolator",
                 "layout", "mipmap", "menu", "font", "raw", "xml"]

"""
    主要作用：复制资源，复制的资源不进行二次public.xml注册，避免缺少sdk资源文件导致项目编译不过去问题。
"""


def copyMissRes(from_dir, copyResDir, to_dir):
    attrDict = findResAttr(from_dir)
    save2File(attrDict, "sdkRes.json")
    transFolderCopy(f"{copyResDir}/res", f"{to_dir}/res", attrDict)
    print(f"执行程序结束")


def findResAttr(from_dir):
    attrDict = {}
    file_list = glob.glob(pathname=from_dir + "/**/R$*smali", recursive=True)
    for filePath in file_list:
        fileName = os.path.basename(filePath)
        fileType = filePath.split("$")[1].split(".")[0]
        if fileType in checkTypeList:
            if attrDict.get(fileType) is None:
                attrDict[fileType] = []

            with open(filePath, encoding="utf-8", mode="r") as rf:
                lines = rf.readlines()
                for line in lines:
                    if line.startswith(".field public static"):
                        attrName = line.split(":")[0].split(" ")[-1]
                        attrValue = line.split("=")[-1].strip()
                        if attrName not in attrDict.get(fileType):
                            attrDict[fileType].append(attrName)

    return attrDict


def transFolderCopy(from_dir, to_dir, mappingData):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        tpath = os.path.join(to_dir, fname)
        if os.path.isdir(fpath):
            transFolderCopy(fpath, tpath, mappingData)
        elif os.path.isfile(fpath):
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
                drawableList = mappingData.get("drawable")
                # 在copy列表中，并且目标文件夹不存在则进行copy操作
                if fileName in drawableList and not fname in folderList:
                    shutil.copy(fpath, tpath)
            elif folderName in checkTypeList:
                otherFileList = mappingData.get(folderName)
                # 在copy列表中，并且目标文件夹不存在则进行copy操作
                if fileName in otherFileList and not fname in folderList:
                    shutil.copy(fpath, tpath)


def save2File(dataList, fpath):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，文件保存在:{fpath}")


def parsePublic(fpath):
    temp = {}
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrType = attrib.get("name")
        if attrType is None or attrName is None:
            continue
        if temp.get(attrType) is None:
            temp[attrType] = []
        if attrName not in temp.get(attrType):
            temp[attrType].append(attrName)
    return temp


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.20.76/DecodeCode/Whatsapp_v2.23.20.76/smali_classes7"
    to_dir = from_dir[0:from_dir.index("/smali")]
    copyResDir = "/Users/shareit/work/androidProjects/AD/app-debug"
    copyMissRes(from_dir, copyResDir, to_dir)
