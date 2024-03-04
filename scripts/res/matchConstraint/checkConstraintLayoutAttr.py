import os
import xml.etree.ElementTree as ET

# android命名空间约束
android_scheme = "http://schemas.android.com/apk/res/android"

"""
    主要作用：检查所有 XML 文件中检查是否缺少ConstraintLayout 属性
"""


def extract_all_attributes(xml_path, all_attributes_set):
    ET.register_namespace('android', android_scheme)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for elem in root.iter():
        for attr in elem.attrib:
            if attr.__contains__('}'):
                newAttr = attr[attr.index('}') + 1:]
                all_attributes_set.add(newAttr)


def tranverseFolder(from_dir, all_attributes_set):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath):
            tranverseFolder(fpath, all_attributes_set)
        elif os.path.isfile(fpath):
            if fname.endswith(".xml"):
                extract_all_attributes(fpath, all_attributes_set)


def check_all_files(xml_directory, key_attributes):
    all_attributes_set = set()
    missing_attributes_set = set()
    tranverseFolder(xml_directory, all_attributes_set)
    # 检查是否包含关键属性
    missing_attributes = key_attributes.difference(all_attributes_set)
    if missing_attributes:
        missing_attributes_set.update(missing_attributes)
    return missing_attributes_set


def loadXmlAttr():
    key_attributes = set()
    # 加载XML文件
    tree = ET.parse('constraintAttr.xml')  # 替换为你的XML文件路径
    root = tree.getroot()
    # 遍历XML文档的元素
    for element in root:
        attr = element.text
        key_attributes.add(attr)
    return key_attributes


if __name__ == "__main__":
    # 指定XML文件目录
    xml_directory = "/Users/shareit/work/shareit/gbwhatsapp_2.24.7.79/DecodeCode/Whatsapp_v2.24.7.79"
    # xml_directory = "/Users/shareit/work/shareit/gbwhatsapp_2.23.20.76/DecodeCode/Whatsapp_v2.23.20.76"
    # xml_directory = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"

    # 检查所有XML文件缺少的关键属性
    missing_attributes_set = check_all_files(f"{xml_directory}/res/layout", loadXmlAttr())

    if missing_attributes_set:
        print("所有XML文件缺少的关键属性:")
        for attr in missing_attributes_set:
            print(attr)
    else:
        print("所有XML文件都包含指定的关键属性.")
