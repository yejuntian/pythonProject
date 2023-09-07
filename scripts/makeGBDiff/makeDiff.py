import codecs
import json
import os
import xml.etree.ElementTree as ET
from convert_wa import convertWA
from renameFiles import replaceRes
from replace_package import replacePackage

# 黑名单，不需要二次重命名
blackTypeStr = ["bool", "drawable", "font", "id", "raw",
                "interpolator", "mipmap", "transition"]
# 存放public.xml映射关系
mappingStr = {}
# 是否要保存测试文件
enableSaveFile = False

"""
    主要作用：重命名项目中res目录下的资源文件，
    与竞品资源文件命名规则保持一致，方便xml资源比对。
"""


def addMapping(fpath):
    parser = ET.parse(fpath)
    root = parser.getroot()

    for child in root:
        attrib = child.attrib
        type = attrib.get("type")
        name = attrib.get("name")
        id = attrib.get("id")
        if id is None or type is None or name is None or type in blackTypeStr:
            continue
        if mappingStr.get(type) is None:
            mappingStr[type] = []
        if name.startswith("APKTOOL_DUMMYVAL_0x7f"):
            newName = getNewName(type, id)
            mappingStr[type].append({name: newName})
    if enableSaveFile:
        save2File(mappingStr, f"{mCurrentPath}/scripts/makeGBDiff/mapping.json")


def save2File(dataList, fpath):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束，文件保存在:{fpath}")


def getNewName(type, id):
    newId = id[6:]
    if type == "string":
        type = "str"
    return f"{type}{newId}"


def main(from_dir, currentPath, isConsole=True):
    global mCurrentPath
    mCurrentPath = currentPath
    filePath = f"{from_dir}/res/values/public.xml"
    addMapping(filePath)
    replacePackage(from_dir)
    replaceRes(from_dir, mappingStr)
    convertWA(from_dir, mCurrentPath, isConsole)


if __name__ == "__main__":
    mCurrentPath = os.getcwd()
    from_dir = "/Users/shareit/work/GBWorke/gbwhatsapp_2.23.13.76/DecodeCode/Whatsapp_2.23.13.76"
    main(from_dir, os.getcwd())
