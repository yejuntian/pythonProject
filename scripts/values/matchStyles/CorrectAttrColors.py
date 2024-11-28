import codecs
import os
import re
import xml.etree.ElementTree as ET

# 匹配android:color="?colorPrimary"或android:textColor="?primary_text"
regexStrList = [r"Color\=\"\?(\w+)\"", r"color\=\"\?(\w+)\""]
# 用于保存xml color属性
attrColorList = set()

"""
    主要作用：匹配values/attrs.xml文件中color属性是否含有format="color"，没有的进行矫正。
"""


def matchAttrColor(from_dir):
    transFolder(f"{from_dir}/res")
    parserAttrs(f"{from_dir}/res/values/attrs.xml")


def transFolder(from_dir):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath):
            transFolder(fpath)
        elif fname.split(".")[-1] == "xml":
            with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
                data = rf.read()
                for regex in regexStrList:
                    matches = re.finditer(regex, data, re.MULTILINE)
                    for matchNum, match in enumerate(matches, start=1):
                        attrColorList.add(match.group(1))


def parserAttrs(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        attr = child.attrib
        attrName = attr.get("name")
        attrFormat = attr.get("format")
        if attrName is None or attrFormat is None:
            continue
        if attrName in attrColorList and not attrFormat.__contains__("color"):
            attr["format"] = f"{attrFormat}|color"
            print(f"attrName = {attrName} attrFormat = {attrFormat}")
    data_str = ET.tostring(root, encoding="utf-8").decode('utf-8')
    write_2_file(fpath, data_str)


def write_2_file(file_path, data_str):
    xml_data = f'<?xml version="1.0" encoding="utf-8"?>\n{data_str}'
    try:
        with codecs.open(file_path, mode='w+', encoding="utf-8") as f:
            f.write(xml_data)
    except Exception as result:
        print(f"写入{file_path}异常: {result}")


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.23.78/DecodeCode/Whatsapp_v2.24.23.78"
    matchAttrColor(from_dir)
