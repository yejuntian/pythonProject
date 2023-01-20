import argparse
import codecs
import json
import os
import re
import xml.etree.ElementTree as ET

# 寻找符合android:id="@id/eula_title"格式的正则
matchRes = r"\"@\w+\/.*?\""
# 只匹配下面的文件类型
extends = ["xml"]
""" 
 主要作用查找：GBWhatsApp xml文件中所有以matchRes正则格式的字符串（例如："@id/eula_title"），
 并检索目标项目中是否以上格式的字符串，并把未找到的输出到StyleNotFind.json文件中
 from_dir:GBWhatsApp项目的diff文件夹
 to_dir:目标项目
"""


def findStyle(from_dir, to_dir):
    allValues = set()
    findValues(f"{from_dir}/res", allValues)
    # Modify_attr.json是手动修改layout.xml文件diff代码
    jsonPath = f"{mCurrentPath}/scripts/values/matchStyles/Modify_attr.json"
    mappingData = getSearchByHandle(jsonPath, getValuesMapping(allValues))
    matchValues(f"{to_dir}/res/values/public.xml", mappingData)


# 手动查找的属性name
def getSearchByHandle(fpath, mappingData):
    with codecs.open(fpath, "r", "utf-8") as rf:
        dict_values = json.loads(rf.read())
        for attrType, attrNameList in dict_values.items():
            nameList = mappingData.get(attrType)
            if nameList is None or len(nameList) <= 0:
                mappingData[attrType] = []
                mappingData[attrType].extend(attrNameList)
            else:
                for attrName in attrNameList:
                    if not attrName in nameList:
                        mappingData[attrType].append(attrName)
    return mappingData


# 查询所有匹配正则的字符串
def findValues(from_dir, allValues):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath):
            findValues(fpath, allValues)
        elif os.path.isfile(fpath):
            if fname.split(".")[-1] in extends:
                print(fpath)
                with codecs.open(fpath, "r", "utf-8") as rf:
                    data = rf.read()
                    matches = re.finditer(matchRes, data, re.MULTILINE)
                    for matchNum, match in enumerate(matches, start=1):
                        allValues.add(match.group())


def getValuesMapping(allValues):
    regex = r"\"@(\w+)\/(.*?)\""
    valuesDict = {}
    for value in allValues:
        matches = re.finditer(regex, value, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            type = match.group(1)
            name = match.group(2)
            # print(f"value = {value} type = {type} name = {name}")
            if valuesDict.get(type) is None:
                valuesDict[type] = []
            valuesDict[type].append(name)
    return valuesDict


def matchValues(fpath, mappingData):
    parse = ET.parse(fpath)
    root = parse.getroot()
    public_dict = {}
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrType = attrib.get("type")
        if attrName is None:
            continue
        if public_dict.get(attrType) is None:
            public_dict[attrType] = []
        public_dict[attrType].append(attrName)

    # 查询没有匹配的属性值
    temp_dict = {}
    for attrType, nameList in mappingData.items():
        # 创建映射关系集合对象
        if temp_dict.get(attrType) is None:
            temp_dict[attrType] = []
        # 匹配属性name
        attrNameList = public_dict.get(attrType)
        if attrNameList is None:
            continue
        for attrName in nameList:
            if not attrName in attrNameList:
                temp_dict[attrType].append(attrName)

    # 没有找到的属性保存到NotFind.json文件中
    save2File(temp_dict, f"{mCurrentPath}/scripts/values/matchStyles/StyleNotFind.json")


def save2File(dataList, fileName):
    jsonStr = json.dumps(dataList, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"执行程序结束,结果保存到：{os.path.join(os.getcwd(), fileName)}")


if __name__ == "__main__":
    mCurrentPath = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    to_dir = args.to_dir
    # from_dir = "/Users/shareit/work/shareit/wa_diff_gb/wa_diff_gbv17_copy_diff"
    # to_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.22.24.78"
    findStyle(from_dir, to_dir)
