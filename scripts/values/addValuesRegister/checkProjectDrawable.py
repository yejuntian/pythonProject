import xml.etree.ElementTree as ET
import os

publicDic = {}
# 项目中res/drawable所有图片集合
drawableSetList = set()

"""
    主要作用:查找项目中注册的drawable资源图片是否存在。
"""


def checkProjectDrawableExit(from_dir):
    parserPublic(f"{from_dir}/res/values/public.xml")
    parserDrawableXml(f"{from_dir}/res/values/drawables.xml")
    transFolder(f"{from_dir}/res", drawableSetList)
    missing_in_set = getDiffDrawable()
    print("**********程序执行结束，缺少的图片如下：**********")
    print(missing_in_set)


def getDiffDrawable():
    drawableSet = set(publicDic.get("drawable"))
    return drawableSet.difference(drawableSetList)


def transFolder(folderPath, drawableSetList):
    listdir = os.listdir(folderPath)
    for fname in listdir:
        fpath = os.path.join(folderPath, fname)
        print(fpath)
        if os.path.isdir(fpath):
            transFolder(fpath, drawableSetList)
        elif os.path.isfile(fpath):
            fileName = fname.split(".")[0]
            folderName = fpath.split("/")[-2]
            if folderName.__contains__("-"):
                folderName = folderName.split("-")[0]
            if folderName == "mipmap" or folderName == "drawable":
                drawableSetList.add(fileName)


def parserDrawableXml(fpath):
    if os.path.exists(fpath):
        parse = ET.parse(fpath)
        root = parse.getroot()
        for child in root:
            attrib = child.attrib
            attrName = attrib.get("name")
            if attrName is None:
                continue
            drawableSetList.add(attrName)


def parserPublic(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrType = attrib.get("type")
        if attrName is None or attrType is None:
            continue
        if publicDic.get(attrType) is None:
            publicDic[attrType] = []
        publicDic[attrType].append(attrName)


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.11.79/DecodeCode/Whatsapp_v2.24.11.79"
    checkProjectDrawableExit(from_dir)
