import os
import xml.etree.ElementTree as ET

data_map = map()


def load_data(xml_path):
    parse = ET.parse(xml_path)
    root = parse.getroot()
    data_list = []
    for element in root:
        data_list.append(element.text)
    return data_list



def merge_values_modify(from_dir):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath) and fpath.__contains__("values"):
            merge_values_modify(fpath)
        elif os.path.isfile(fpath):
            pass


if __name__ == "__main__":
    dir = "/Users/shareit/work/shareit/wa_diff_gb/whatsapp_2.22.22.80"
    load_data("scripts/replace_icon/diff_attrs.xml")
    merge_values_modify(dir)


class ValuesAttrs:
    def __init__(self, parentTagName, subTag, subTagName, subTagTxt):
        self.parentTagName = parentTagName  # 父标签属性name
        self.subTag = subTag  # 子标签tag
        self.subTagName = subTagName  # 子标签属性name
        self.subTagTxt = subTagTxt  # 子标签文本内容
