import argparse
import glob
import os
import shutil
import traceback
import lxml.etree as ET
import merge_public

"""
    对比两个不同项目values目录下xml不同，
    查找diff不同处，并把diff复制到对应目标文件。
"""


def traverse_folder(project_from_dir, project_to_dir):
    rex_str = os.sep + "res" + os.sep + "values*" + os.sep + "**"
    from_data_list = glob.glob(project_from_dir + rex_str)
    for from_path in from_data_list:
        from_file_name = os.path.basename(from_path)
        from_sub_dir = from_path[len(project_to_dir):from_path.rindex(os.sep)]

        to_dir = project_to_dir + os.sep + "res" + os.sep + from_sub_dir
        to_path = str(to_dir) + os.sep + from_file_name

        # 目标文件夹不存在，创建新文件夹
        if not os.path.exists(to_dir):
            os.makedirs(to_dir, exist_ok=True)
            # copy当前新文件
            shutil.copy(from_path, to_dir)
        merge_diff(from_path, to_path)


# 合并diff属性到目标文件xml中
def merge_diff(from_path, to_path):
    if not os.path.isfile(to_path):
        shutil.copy(from_path, to_path)
    else:
        # 目标文件
        to_parse = ET.parse(to_path)
        to_root = to_parse.getroot()
        # 目标xml文件，标签集合map
        to_root_map = {}
        # 两个xml，diff标签集合map
        new_add_list = []
        for to_child in to_root:
            child_str = ET.tostring(to_child, encoding="utf-8").decode('utf-8').strip()
            if not child_str.startswith("<!--"):
                to_attr_name = to_child.attrib["name"]
                to_root_map[to_attr_name] = to_child

        # 源文件
        from_parse = ET.parse(from_path)
        from_root = from_parse.getroot()
        isChanged: bool = False
        for from_child in from_root:
            from_attr_name = from_child.attrib["name"]
            if from_attr_name not in to_root_map and "APKTOOL" not in from_attr_name:
                to_root.append(from_child)
                new_add_list.append(from_child)
                isChanged = True
        if isChanged:
            xml_content = convert_str(to_root)
            # 合并public.xml
            if os.path.basename(to_path) == "public.xml":
                merge_public.copy_attrs(from_path, to_path)
            else:
                # 合并其他xml
                save_2_file(xml_content, to_path)


# 把diff标签输出到其他文件中
def merge_diff_attrs(from_path, to_path, target_project_path):
    diff_dir = str(to_path)
    diff_project_path = f'{target_project_path}_diff{diff_dir.replace(target_project_path, "")}'
    diff_folder_path = os.path.dirname(diff_project_path)

    # 创建目标目录文件夹,并copy文件
    if not os.path.exists(to_path):
        if not os.path.exists(diff_folder_path):
            os.makedirs(diff_folder_path, exist_ok=True)
        shutil.copy(from_path, diff_folder_path)
    else:
        # 目标文件
        to_parse = ET.parse(to_path)
        to_root = to_parse.getroot()
        # 目标xml文件，标签集合map
        to_root_map = {}
        # 两个xml，diff标签集合map
        new_add_list = []
        for to_child in to_root:
            to_attr_name = to_child.attrib["name"]
            to_root_map[to_attr_name] = to_child

        # 源文件
        from_parse = ET.parse(from_path)
        from_root = from_parse.getroot()
        isChanged: bool = False
        for from_child in from_root:
            from_child_str = ET.tostring(from_child, encoding="utf-8").decode('utf-8').strip()
            if not from_child_str.startswith("<!--"):
                from_attr_name = from_child.attrib["name"]
                if from_attr_name not in to_root_map and "APKTOOL" not in from_attr_name:
                    new_add_list.append(from_child)
                    isChanged = True
        if isChanged:
            xml_content = convert_str(new_add_list)

            if not os.path.exists(diff_folder_path):
                os.makedirs(diff_folder_path, exist_ok=True)
            save_2_file(xml_content, diff_project_path)


def convert_str(to_root):
    xml_content: str = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    for child in to_root:
        attr_tag = child.tag
        text = child.text
        xml_content += "    "
        # string标签中text内容">"会被转移为'&gt'
        if attr_tag == "string" and str(text).__contains__(">"):
            child_str = ET.tostring(child, encoding="utf-8").decode('utf-8').strip().replace('&gt;', '>')
            xml_content += child_str
        else:
            xml_content += ET.tostring(child, encoding='utf-8').decode('utf-8').strip().replace('/>', ' />')
        xml_content += '\n'

    xml_content += '</resources>\n'
    return xml_content


def save_2_file(data_str, target_file_path):
    try:
        with open(target_file_path, 'w+') as f:
            f.write(data_str)
    except Exception as result:
        print(f"写入{target_file_path}出现异常: {result}")
        print(traceback.format_exc())
    # else:
        # print(f"写入{target_file_path}完成")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_from_dir")
    parser.add_argument("project_to_dir")
    args = parser.parse_args()
    traverse_folder(args.project_from_dir, args.project_to_dir)
