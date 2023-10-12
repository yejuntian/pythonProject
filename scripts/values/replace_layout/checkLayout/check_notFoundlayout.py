import xml.etree.ElementTree as ET
import json
import os
import codecs

"""
    主要作用：根据modify_layout.xml配置列表，匹配项目res/layout目录下所有的xml文件
    没有找到xml输出保存到notFoundLayout.json文件中
"""


def checkNotFoundLayout(from_dir):
    modifyNameList = loadData(f"{os.getcwd()}/scripts/values/replace_layout/checkLayout/modify_layout.xml")
    nameList = parserPublic(f"{from_dir}/res/values/public.xml")
    dataList = []
    for modifyName in modifyNameList:
        if not modifyName in nameList:
            dataList.append(modifyName)
    save2File(os.getcwd(), dataList, "notFoundLayout.json")


def save2File(folder_path, dataList, fileName):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    savePath = os.path.join(folder_path, fileName)
    with codecs.open(savePath, "w", "utf-8") as wf:
        wf.write(jsonStr)
    print(f"结果保存到：{savePath}")


def loadData(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    data_list = []
    for child in root:
        name = child.text
        data_list.append(name.split(".")[0])
    return data_list


def parserPublic(fpath):
    parser = ET.parse(fpath)
    root = parser.getroot()
    namelist = []
    for child in root:
        attrib = child.attrib
        name = attrib.get("name")
        type = attrib.get("type")
        if not name is None and not type is None and type == "layout":
            namelist.append(name)
    return namelist


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.23.2.76"
    checkNotFoundLayout(from_dir)
