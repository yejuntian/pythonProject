import os
import xml.etree.ElementTree as ET
import argparse

"""
    主要作用：检查所有 XML 文件中检查是否缺少ConstraintLayout 属性
"""


def loadXmlAttr():
    key_attributes = set()
    # 加载XML文件
    tree = ET.parse(f'{os.getcwd()}/scripts/res/matchConstraint/constraintAttr.xml')  # 替换为你的XML文件路径
    root = tree.getroot()
    # 遍历XML文档的元素
    for element in root:
        attr = element.text
        key_attributes.add(attr)
    return key_attributes


def secondCheck(fpath, constranintLayoutAttrs):
    missing_attrSet = set()
    tree = ET.parse(fpath)
    root = tree.getroot()
    allAttrs = set()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        if attrName is not None and not attrName.startswith("APKTOOL_DUMMYVAL"):
            allAttrs.add(attrName)
    for attr in constranintLayoutAttrs:
        if attr not in allAttrs:
            missing_attrSet.add(attr)
    return missing_attrSet


# 检查按个属性重命名错误
def checkRepeatAttr(fpath, missAttrs):
    repeat_attrSet = set()
    tree = ET.parse(fpath)
    root = tree.getroot()
    allPublicAttrs = set()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        if attrName is not None and not attrName.startswith("APKTOOL_DUMMYVAL"):
            allPublicAttrs.add(attrName)
    for attr in missAttrs:
        if attr in allPublicAttrs:
            repeat_attrSet.add(attr)
    return repeat_attrSet


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # 项目目录
    # from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.19.86/DecodeCode/Whatsapp_v2.24.19.86"

    # 检查所有XML文件缺少的关键属性
    xml_attr = loadXmlAttr()
    missing_attributes_set = secondCheck(f"{from_dir}/res/values/attrs.xml", xml_attr)
    repeatAttrs = checkRepeatAttr(f"{from_dir}/res/values/public.xml", missing_attributes_set)
    if missing_attributes_set:
        print("所有XML文件缺少的关键属性:")
        for attr in missing_attributes_set:
            print(attr)
        if len(repeatAttrs) > 0:
            print("错误重命名属性如下:")
            for attr in repeatAttrs:
                print(attr)
    else:
        print("所有XML文件都包含指定的关键属性.")
