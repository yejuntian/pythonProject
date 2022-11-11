import argparse
import codecs
import lxml.etree as ET

"""
    主要作用：比较两个public.xml不同,
    并把新增属性输出到目标文件中
"""

# 用于存放每种类型的最大值;key是类型,value是最大值
max_dict = {}
# key是类型，value是key类型对应的数组集合
name_dict = {}


def copy_attrs(from_dir, to_dir):
    to_tree = ET.parse(to_dir)
    to_root = to_tree.getroot()
    for child in to_root:
        if child.tag == "public" and "id" in child.attrib:
            attr_name = str(child.attrib['name']).strip()
            attr_type = child.attrib['type'].strip()
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
    from_tree = ET.parse(from_dir)
    from_root = from_tree.getroot()
    for child in from_root:
        if child.tag == "public" and "id" in child.attrib:
            child_name = child.attrib['name'].strip()
            child_type = child.attrib['type'].strip()
            # 屏蔽APKTOOL开头的name
            if child_name not in name_dict[child_type] and "APKTOOL" not in child_name:
                child_max = max_dict[child_type]
                child.set('id', str(hex(int(child_max.attrib['id'], 16) + 1)))
                max_dict[child_type] = child
                index = to_root.index(child_max)
                to_root.insert(index + 1, child)
    save_to_file(to_root, to_dir)


def save_to_file(data_list, file_name):
    # print(file_name)
    with codecs.open(file_name, "w+", encoding="utf-8") as wf:
        wf.write('<?xml version="1.0" encoding="utf-8"?>\n')
        wf.write('<resources>\n')
        for child in data_list:
            attr = child.attrib
            wf.write(f'    <public type="{attr["type"]}" name="{attr["name"]}" id="{attr["id"]}" />\n')
        wf.write('</resources>')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    #目标public.xml绝对地址
    parser.add_argument("to_dir")
    options = parser.parse_args()
    copy_attrs(options.from_dir, options.to_dir)
    print(f"输出结果到：{options.to_dir}")
