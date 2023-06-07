import codecs
import json
import os
import re
import xml.etree.ElementTree as ET

# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'kotlin', 'lib', 'META-INF',
             'original', 'AndroidManifest.xml', 'apktool.yml']
# 只匹配下面的文件类型
extends = ["smali", "xml"]
# 正则匹配字符串
reStr = "0x[0-9A-Za-z]{8}"
# 要查找的文件集合
filelist = []
# 目标文件地址1
target_path1 = "smali_classes5/com/gbwhatsapp/yo/d1.smali"
# 目标文件地址2
target_path2 = "res/values/public.xml"


def findIds(from_dir):
    ids = getAllIds(os.path.join(from_dir, target_path1))
    attrMap = getAttrs(ids, os.path.join(from_dir, target_path2))
    save_2_file(attrMap)


def getAllIds(fpath):
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = rf.read()
    return re.findall(reStr, data, re.MULTILINE)


def getAttrs(ids, fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    attrMap = {}
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrType = attrib.get("type")
        attrId = attrib.get("id")
        if not attrType is None and not attrName is None and not attrId is None:
            if attrId in ids:
                if attrMap.get(attrType) is None:
                    attrMap[attrType] = []
                attrMap[attrType].append(attrName)
    return attrMap


def save_2_file(attrMap):
    folder_path = os.getcwd()
    for key in attrMap.keys():
        fileName = f"{key}.json"
        jsonStr = json.dumps(attrMap[key], ensure_ascii=False, indent=2)
        with open(fileName, "w+") as wf:
            wf.write(jsonStr)
        print(f"执行程序结束,结果保存到：{os.path.join(folder_path, fileName)}")


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    findIds(from_dir)
