import codecs
import json
import os
import argparse
import xml.etree.ElementTree as ET

# 用于存放xml文件名字和重复name属性的对应关系
repeatNameDict = {}

"""
    主要作用：查找string.xml、styles.xml、colors.xml
    是否存在重复的name
"""


def checkRepeatName(from_dir):
    transFolder(from_dir)
    isExit = False
    for attrType, attrList in repeatNameDict.items():
        if len(attrList) > 0:
            isExit = True

    if isExit:
        save_2_file(repeatNameDict, f"{os.getcwd()}/scripts/values/repeatName.json")
    else:
        print(f"*** {from_dir} *** 不存在重复的属性name")


def transFolder(from_dir):
    if os.path.isdir(from_dir):
        listdir = os.listdir(from_dir)
        for fname in listdir:
            fpath = os.path.join(from_dir, fname)
            if os.path.isdir(fpath):
                transFolder(from_dir)
            elif os.path.isfile(fpath) and not fname == "public.xml":
                findRepeatName(fpath, fname.split(".")[0])
    else:
        findRepeatName(from_dir, from_dir.split(".")[0])


def findRepeatName(fpath, attrType):
    if repeatNameDict.get(attrType) is None:
        repeatNameDict[attrType] = []

    parser = ET.parse(fpath)
    root = parser.getroot()
    # 用于存放重复的name
    repeatNameList = []
    # 用于存放所有name
    nameList = []
    for child in root:
        attrib = child.attrib
        name = attrib.get("name")
        if name is None:
            continue
        if name not in nameList:
            nameList.append(name)
        else:
            repeatNameList.append(name)
    repeatNameDict[attrType] = repeatNameList


def save_2_file(dataList, fpath):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"程序执行结束，结果保存在：{fpath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # from_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.22.24.78"
    checkRepeatName(f"{from_dir}/res/values")
