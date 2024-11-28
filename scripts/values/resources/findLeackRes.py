import argparse
import codecs
import json
import os
import xml.etree.ElementTree as ET

# whatsApp所有属性集合
resDict = {}
"""
 主要作用：解析from_dir/values/public.xml，对比whatsapp.json查看public.xml少了哪些属性值
"""


def findLeackRes(from_dir, to_dir):
    publicResDic = parserPublic(f"{to_dir}/res/values/public.xml")
    setJsonData(from_dir, publicResDic)
    save2File(resDict, os.getcwd(), "diff.json")


def setJsonData(fpath, publicResDic):
    with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
        tempDict = json.loads(rf.read())
        for type, nameList in tempDict.items():
            if resDict.get(type) is None:
                resDict[type] = []
            for name in nameList:
                if name not in publicResDic.get(type) and name not in resDict.get(type):
                    resDict[type].append(name)


def parserPublic(fpath):
    parser = ET.parse(fpath)
    root = parser.getroot()
    tempDict = {}
    for child in root:
        attrib = child.attrib
        attrType = attrib.get("type")
        attrName = attrib.get("name")
        if attrType is None or attrName is None:
            continue
        if tempDict.get(attrType) is None:
            tempDict[attrType] = []
        else:
            tempDict[attrType].append(attrName)
    return tempDict


def save2File(dataList, folder_path, fileName):
    os.chdir(folder_path)
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,结果保存到：{os.path.join(folder_path, fileName)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # from_dir = "/Users/shareit/work/pythonProject/scripts/values/resources/gb_needcopy_res.json"
    from_dir = "/Users/shareit/work/pythonProject/scripts/values/resources/whatsapp.json"
    to_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.23.78/DecodeCode/Whatsapp_v2.24.23.78"
    findLeackRes(from_dir, to_dir)
