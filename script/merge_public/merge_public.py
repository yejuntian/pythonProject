import argparse
import xml.etree.ElementTree as ET
import codecs

"""
    主要作用：比较两个public.xml不同
"""

# 用于存放每种类型的最大值key是类型value是最大值
max_dict = {}
# key是类型value是名字集合
name_dict = {}


# 解析public.xml
def copy_attrs(from_dir, to_dir):
    to_tree = ET.parse(to_dir)
    for child in to_tree.getroot():
        if child.tag == "public" and "id" in child.attrib:
            name = child.attrib['name']
            type = child.attrib['type']
            id = child.attrib['id']
            if type in name_dict:
                pass
            else:
                name_dict[type] = []
            name_dict[type].append(name)
            # 十六进制转十进制
            id = int(id, 16)
            if type in max_dict:
                if id > int(max_dict[type].attrib['id'], 16):
                    max_dict[type] = child
            else:
                max_dict[type] = child

    from_tree = ET.parse(from_dir)
    for child in from_tree.getroot():
        if child.tag == "public" and "id" in child.attrib:
            name = child.attrib['name']
            type = child.attrib['type']
            # 屏蔽APKTOOL开头的name
            if name not in name_dict[type] and "APKTOOL" not in name:
                max = max_dict[type]
                child.set('id', str(hex(int(max.attrib['id'], 16) + 1)))
                max_dict[type] = child
                index = to_tree.getroot().index(max)
                to_tree.getroot().insert(index + 1, child)
    save_to_file(to_tree.getroot(), to_dir)


def save_to_file(data_list, file_name):
    print(file_name)
    with codecs.open(file_name, "w+", encoding="utf-8") as wf:
        wf.write('<?xml version="1.0" encoding="utf-8"?>\n')
        wf.write('<resources>\n')
        for child in data_list:
            attr = child.attrib
            wf.write(f'    <public type="{attr["type"]}" name="{attr["name"]}" id="{attr["id"]}" />\n')
        wf.write('</resources>')


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("from_dir")
    # parser.add_argument("to_dir")
    # options = parser.parse_args()
    # copy_attrs(options.from_dir, options.to_dir)
    copy_attrs("/Users/tianyejun/work/pythonWrokSpace/pythonProject/workSpace/public.xml",
               "/Users/tianyejun/work/pythonWrokSpace/pythonProject/workSpace/public1.xml")
