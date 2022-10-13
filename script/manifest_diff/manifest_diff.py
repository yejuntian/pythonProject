import argparse
import codecs
import os
import xml.etree.ElementTree as ET

android_scheme = "http://schemas.android.com/apk/res/android"
# 用于存储权限的集合；
permission_data_list = []
# 用于存四大组件的集合；
component_data_list = []
# 用于存储权限的集合的diff；
permission_list_diff = []
# 用于存四大组件的集合的diff；
component_list_diff = []

"""
    主要作用：对比两个AndroidManifest.xml查找不同处，并输出diff到新的xml中。
"""


# 查找manifest 不同之处，并保存到另外一个文件中
def merge_manifest_diff(from_dir, to_dir):
    parse_old_manifest(from_dir)
    parse_new_manifest(to_dir)
    save_2_file(to_dir)


def parse_old_manifest(from_dir):
    # ET.register_namespace("android", android_scheme)
    parse = ET.parse(from_dir)
    from_root = parse.getroot()

    for child in from_root:
        child_tag = child.tag
        # 特殊处理
        if child_tag == "queries":
            permission_data_list.append(child_tag)
            continue

        nameSpace = "{" + android_scheme + "}"
        child_name = child.attrib[f"{nameSpace}name"]
        if child_tag != "application":
            permission_data_list.append(child_name)
        else:
            for sub_child in child:
                sub_child_name = sub_child.attrib[f"{nameSpace}name"]
                component_data_list.append(sub_child_name)


def parse_new_manifest(to_dir):
    ET.register_namespace("android", android_scheme)
    parse = ET.parse(to_dir)
    to_root = parse.getroot()

    for child in to_root:
        child_tag = child.tag
        # 特殊处理
        if child_tag == "queries" and child_tag not in permission_data_list:
            permission_list_diff.append(child)
            continue

        nameSpace = "{" + android_scheme + "}"
        child_name = child.attrib[f"{nameSpace}name"]
        # 过滤更换包名导致的diff
        new_child_name = child_name.replace("whatsapp", "gbwhatsapp")
        if child_tag != "application":
            if child_name not in permission_data_list and new_child_name not in permission_data_list:
                permission_list_diff.append(child)
        else:
            for sub_child in child:
                sub_child_name = sub_child.attrib[f"{nameSpace}name"]
                # 过滤更换包名导致的diff
                new_sub_child_name = sub_child_name.replace("gbwhatsapp", "whatsapp")
                if sub_child_name not in component_data_list and new_sub_child_name not in component_data_list:
                    component_list_diff.append(sub_child)


def save_2_file(to_dir):
    namespace = 'xmlns:android="http://schemas.android.com/apk/res/android"'
    xml_content: str = '<?xml version="1.0" encoding="utf-8"?>\n<manifest>\n '
    for permission in permission_list_diff:
        xml_content += "    " + ET.tostring(permission, encoding='utf-8').decode('utf-8').strip().replace(' />', '/>')
        xml_content = xml_content.replace(f'{namespace} ', "")
        xml_content = xml_content.replace(namespace, "")
        xml_content += '\n'

    xml_content += '    <application>\n'
    for child in component_list_diff:
        xml_content += "        " + ET.tostring(child, encoding='utf-8').decode('utf-8').strip().replace(' />', '/>')
        xml_content = xml_content.replace(f'{namespace} ', "")
        xml_content = xml_content.replace(namespace, "")
        xml_content += '\n'

    xml_content += '    </application>\n</manifest>\n'

    file_path = to_dir
    if os.path.exists(file_path):
        dir_path = os.path.dirname(file_path)
        file_path = f"{dir_path}/AndroidManifest_diff.xml"
    with codecs.open(file_path, mode="w", encoding="utf-8") as wf:
        wf.write(xml_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("fro_dir")
    parser.add_argument("to_dir")
    args = parser.parse_args()
    merge_manifest_diff(args.fro_dir, args.to_dir)
