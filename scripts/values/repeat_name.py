import codecs
import json
import os
import xml.etree.ElementTree as ET

# 用于存放重复的name
repeatNameList = []
# 用于存放所有name
nameList = []

"""
    主要作用：查找string.xml、styles.xml、colors.xml
    是否存在重复的name
"""


def findRepeatName(fpath):
    parser = ET.parse(fpath)
    root = parser.getroot()

    for child in root:
        attrib = child.attrib
        name = attrib.get("name")
        if name is None:
            continue
        if name not in nameList:
            nameList.append(name)
        else:
            repeatNameList.append(name)
    fileName = f'{os.path.basename(fpath).split(".")[0]}.json'
    newPath = os.path.join(os.getcwd(), fileName)
    if len(repeatNameList) <= 0:
        print(f"*** {os.path.basename(fpath)} *** 不存在重复的属性name")
    else:
        save_2_file(repeatNameList, newPath)


def save_2_file(dataList, fpath):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with codecs.open(fpath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"程序执行结束，结果保存在：{fpath}")


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/GBWorke/whatsapp_new/Whatsapp_v2.22.24.78/res/values-night/colors.xml"
    findRepeatName(from_dir)
