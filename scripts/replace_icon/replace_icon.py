import argparse
import os
import shutil
import xml.etree.ElementTree as ET

# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'kotlin', 'lib', 'META-INF',
             'original', 'AndroidManifest.xml', 'apktool.yml']
# 要复制的icon列表
icon_list = []

"""
    主要作用：根据"icon_list"图片资源列表，
    遍历复制的目录列表找到对应图片，并替换目标目录对应图片
"""


def delOldIcon(from_path, black_list):
    from_listdir = os.listdir(from_path)
    for file_name in from_listdir:
        from_file_path = os.path.join(from_path, file_name)
        if file_name not in black_list and not file_name.__contains__("smali"):
            if os.path.isdir(from_file_path):
                # 过滤不需要遍历的文件夹
                if enable_traver(file_name, "layout") and enable_traver(file_name, "values") and enable_traver(
                        file_name, "xml"):
                    # print(f"遍历文件：{file_name}")
                    delOldIcon(from_file_path, blacklist)
                else:
                    continue
            else:
                relativePath = os.path.join(from_path[from_path.rindex("/") + 1:], file_name)
                if file_name in icon_list or relativePath in icon_list:
                    os.remove(from_file_path)


def copyIcon(from_path, to_path, black_list):
    from_listdir = os.listdir(from_path)
    for file_name in from_listdir:
        from_file_path = os.path.join(from_path, file_name)
        to_file_path = os.path.join(to_path, file_name)
        if file_name not in black_list and not file_name.__contains__("smali"):
            if os.path.isdir(from_file_path):
                # 过滤不需要遍历的文件夹
                if enable_traver(file_name, "layout") and enable_traver(file_name, "values") and enable_traver(
                        file_name, "xml"):
                    # print(f"遍历文件：{file_name}")
                    copyIcon(from_file_path, to_file_path, blacklist)
                else:
                    continue
            else:
                relativePath = os.path.join(from_path[from_path.rindex("/") + 1:], file_name)
                if file_name in icon_list or relativePath in icon_list:
                    if not os.path.exists(to_path):
                        os.makedirs(to_path, exist_ok=True)
                    # print(file_name)
                    shutil.copyfile(from_file_path, to_file_path)


def enable_traver(file_name, folder_name):
    return not file_name.__contains__(folder_name)


def load_data(xml_path):
    parse = ET.parse(xml_path)
    root = parse.getroot()
    data_list = []
    for element in root:
        data_list.append(element.text)
    return data_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_project_dir")
    parser.add_argument("to_project_dir")
    args = parser.parse_args()

    number = input('请输入默认包名对应的数字：1->com.gbwhatsapp", "2->com.obwhatsapp",'''
                   ' "3->com.WhatsApp2Plus"\n')
    if number == "1":
        icon_list = load_data("scripts/replace_icon/gb_res_icon.xml")
    elif number == "2":
        icon_list = load_data("scripts/replace_icon/ob_res_icon.xml")
    elif number == "3":
        icon_list = load_data("scripts/replace_icon/plus_res_icon.xml")

    delOldIcon(args.to_project_dir, blacklist)
    if not os.path.exists(args.to_project_dir):
        os.makedirs(args.to_project_dir, exist_ok=True)
    copyIcon(args.from_project_dir, args.to_project_dir, blacklist)
    print(f"执行完成，输出结果保存到：{args.to_project_dir}")
