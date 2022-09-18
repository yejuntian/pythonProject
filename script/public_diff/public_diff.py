import argparse
import xml.etree.ElementTree as ET
import os


# 找出反编译apk中public.xml与反编译项目中public.xml不同的资源属性
# 并把输出结果输出到public_diff.xml中


def parser_public_xml(from_dir, to_dir):
    """
        from_dir：需要查询diff的public.xml
        to_dir:项目默认的public.xml
    """
    to_res_tree = ET.parse(to_dir)
    to_root_tree = to_res_tree.getroot()
    des_res_set = set()
    for child in to_root_tree:
        attr_type = child.attrib["type"]
        attr_name = child.attrib["name"]
        des_res_set.add(f"{attr_type}#{attr_name}")

    from_res_tree = ET.parse(from_dir)
    from_root_tree = from_res_tree.getroot()

    xml_label = []
    xml_label.append('<?xml version="1.0" encoding="utf-8" standalone="no"?>')
    xml_label.append('<resources>')
    for child in from_root_tree:
        label_type = child.attrib["type"]
        label_name = child.attrib["name"]
        label_id = child.attrib["id"]
        label_value = f"{label_type}#{label_name}"
        if label_value not in des_res_set and "APKTOOL_DUMMY_" not in label_name:
            sub = f'    <public type="{label_type}" name="{label_name}" id="{label_id}" />'
            xml_label.append(sub)
    xml_label.append('</resources>')

    newFile = f"{os.getcwd()}/public_diff.xml"
    print("*********输出diff文件到下面路径地址*********")
    print("newFile = " + newFile)
    with open(newFile, 'w+') as wf:
        for line in xml_label:
            wf.write(line + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    options = parser.parse_args()

    parser_public_xml(options.from_dir, options.to_dir)

