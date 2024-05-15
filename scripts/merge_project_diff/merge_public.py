import argparse
import codecs
import re
import lxml.etree as ET

"""
    主要作用：比较两个public.xml不同,
    并把新增属性输出到目标文件中
"""

# 用于存放每种类型的最大值;key是类型,value是最大值
max_dict = {}
# key是类型，value是key类型对应的数组集合
name_dict = {}
typeList = ["anim", "animator", "array", "bool", "interpolator",
            "menu", "plurals", "navigation", "raw", "font", "xml"]

# 临时定义的子元素
tempChildList = []


def copy_attrs(from_dir, to_dir):
    to_tree = ET.parse(to_dir)
    to_root = to_tree.getroot()
    lastType = "xml"
    for child in to_root:
        if child.tag == "public" and "id" in child.attrib:
            attr_name = str(child.attrib['name']).strip()
            attr_type = child.attrib['type'].strip()
            lastType = attr_type
            attr_id = child.attrib['id'].strip()
            if attr_type not in name_dict:
                name_dict[attr_type] = set()
            name_dict[attr_type].add(attr_name)
            # 十六进制转十进制
            max_id = int(attr_id, 16)
            if attr_type in max_dict:
                if max_id > int(max_dict[attr_type].attrib['id'], 16):
                    max_dict[attr_type] = child
            else:
                max_dict[attr_type] = child
    addLeackType(lastType, to_root)
    from_tree = ET.parse(from_dir)
    from_root = from_tree.getroot()
    for child in from_root:
        if child.tag == "public" and "id" in child.attrib:
            child_name = child.attrib['name'].strip()
            child_type = child.attrib['type'].strip()
            # 屏蔽APKTOOL开头的name
            if child_name.__contains__("APKTOOL") and not re.match(r"APKTOOL_.*_0x\w{8}", child_name):
                continue
            else:
                if child_name not in name_dict[child_type]:
                    child_max = max_dict[child_type]
                    child.set('id', str(hex(int(child_max.attrib['id'], 16) + 1)))
                    max_dict[child_type] = child
                    index = to_root.index(child_max)
                    to_root.insert(index + 1, child)
    save_to_file(to_root, to_dir)


def addLeackType(lastType, to_root):
    tempTypeList = []
    for attrType in typeList:
        if attrType not in name_dict.keys():
            maxId = max_dict[lastType].attrib['id']
            lastType = attrType
            mid_bits = int(str(maxId[4:6])) + 1
            maxTypeId = hex(int(f"0x7f{mid_bits}0000", 16))

            child = ET.Element("public", type=lastType, id=maxTypeId, name="temp")
            max_dict[lastType] = child
            name_dict[lastType] = set()
            to_root.append(child)

            tempChildList.append(child)
            tempTypeList.append(attrType)

    for attrType in tempTypeList:
        child_max = max_dict[attrType]
        maxId = int(child_max.attrib['id'], 16) - 1
        child_max.set('id', str(hex(maxId)))


def save_to_file(data_list, file_name):
    # print(file_name)
    with codecs.open(file_name, "w+", encoding="utf-8") as wf:
        wf.write('<?xml version="1.0" encoding="utf-8"?>\n')
        wf.write('<resources>\n')
        for child in data_list:
            attr = child.attrib
            attrType = attr["type"]
            attrName = attr["name"]
            attrId = attr["id"]
            if child in tempChildList:
                continue
            wf.write(f'    <public type="{attrType}" name="{attrName}" id="{attrId}" />\n')
        wf.write('</resources>')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    # 目标public.xml绝对地址
    parser.add_argument("to_dir")
    options = parser.parse_args()
    copy_attrs(options.from_dir, options.to_dir)
    print(f"输出结果到：{options.to_dir}")
