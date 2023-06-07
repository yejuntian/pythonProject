import argparse
import os
import re
import xml.etree.ElementTree as ET

# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'kotlin', 'lib', 'META-INF',
             'original', 'AndroidManifest.xml', 'apktool.yml']
# 只匹配下面的文件类型
extends = ["smali", "xml"]
# 正在匹配字符串
reStr = "0x[0-9A-Za-z]{8}"
# 要查找的文件集合
filelist = []
# 目标文件地址1
target_path1 = "com/gbwhatsapp/yo/d1.smali"
# 目标文件地址2
target_path2 = "res/values/public.xml"
# Lcom/gbwhatsapp/yo/d.smali文件values数值列表
old_value_list = []
# Lcom/gbwhatsapp/yo/d.smali文件values数值对应的name列表
old_names_list = []
# 新旧values对应列表
value_entity_list = []

"""
    主要作用：替换Lcom/gbwhatsapp/yo/d.smali;类中字符串对应的values数值
"""


class ValueEntity:
    def __init__(self, oldValue, attrName, newValue):
        self.oldValue = oldValue
        self.attrName = attrName
        self.newValue = newValue

    def __repr__(self) -> str:
        return f"oldValue={self.oldValue} attrName={self.attrName} newValue={self.newValue}"


def replaceValues(from_dir, to_dir):
    transFolder(from_dir, blacklist)
    findValueFromFileList(filelist)
    filelist.clear()
    transFolder(to_dir, blacklist)
    replaceFile(filelist)
    printNotFondValues(value_entity_list)


def transFolder(from_dir, black_list):
    from_listdir = os.listdir(from_dir)
    for file_name in from_listdir:
        from_file_path = os.path.join(from_dir, file_name)
        if file_name not in black_list:
            if os.path.isdir(from_file_path):
                transFolder(from_file_path, black_list)
            elif os.path.isfile(from_file_path):
                if file_name.split('.')[-1] in extends:
                    if from_file_path.__contains__(target_path1) or from_file_path.__contains__(target_path2):
                        filelist.append(from_file_path)


def findValueFromFileList(fileList):
    targetIndex = 0
    for index, fpath in enumerate(fileList):
        if fpath.__contains__(target_path1):
            with open(fpath, mode="r", encoding="utf-8") as rf:
                old_value_list.extend(re.findall(reStr, rf.read()))
        else:
            targetIndex = index

    parse = ET.parse(fileList[targetIndex])
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        attrId = attrib.get("id")
        attrType = attrib.get("type")
        if attrId in old_value_list:
            name = f"{attrType}#{attrName}"
            old_names_list.append(name)
            value_entity_list.append(ValueEntity(attrId, name, "None"))


def replaceFile(fileList):
    targetIndex = 0
    for index, fpath in enumerate(fileList):
        if fpath.__contains__(target_path2):
            parse = ET.parse(fpath)
            root = parse.getroot()
            for child in root:
                attrib = child.attrib
                attrName = attrib.get("name")
                attrId = attrib.get("id")
                attrType = attrib.get("type")
                name = f"{attrType}#{attrName}"
                if name in old_names_list:
                    valueIndex = old_names_list.index(name)
                    valueEntity = value_entity_list[valueIndex]
                    valueEntity.newValue = attrId
        else:
            targetIndex = index
    save_2_file(fileList[targetIndex])


def save_2_file(fpath):
    new_value_list = []
    for entity in value_entity_list:
        new_value_list.append(entity.oldValue)
    result = ""
    with open(fpath, mode="r", encoding="utf-8") as rf:
        for line in rf.readlines():
            findList = re.findall(reStr, line)
            if len(findList) > 0:
                findStr = findList[0]
                entity = value_entity_list[new_value_list.index(findStr)]
                line = line.replace(findStr, entity.newValue)
                result += line
            else:
                result += line
    with open(fpath, mode="w+", encoding="utf-8") as wf:
        wf.write(result)


def printNotFondValues(entityList):
    for bean in entityList:
        if bean.newValue == "None":
            attr_type = bean.attrName.split("#")[0]
            attr_name = bean.attrName.split("#")[1]
            print(f'<public type="{attr_type}" name="{attr_name}" id="NotFound" />')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    args = parser.parse_args()

    from_dir = args.from_dir
    to_dir = args.to_dir
    # from_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/Whatsapp_v2.23.2.76"
    # to_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.8.76/DecodeCode/Whatsapp_v2.23.8.76"
    replaceValues(from_dir, to_dir)
    print(f"执行完成，输出结果保存到：{to_dir}")
