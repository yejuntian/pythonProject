import os
import shutil
import argparse
import xml.etree.ElementTree as ET

# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'kotlin', 'lib', 'META-INF',
             'original', 'AndroidManifest.xml', 'apktool.yml']
# 要复制的icon列表
icon_list = []
iconNameList = ["WhatsApp", "WhatsApp_GB", "WhatsApp_New", "WhatsApp_2023"]

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


# 删除指定icon，并替换为最新icon
def replaceIcon(from_dir, to_dir, configPath):
    iconPath = f"{configPath}/icon_list.xml"
    if os.path.exists(from_dir) and os.path.exists(iconPath):
        global icon_list
        icon_list = load_data(iconPath)
        delOldIcon(to_dir, blacklist)
        copyIcon(from_dir, to_dir, blacklist)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()

    from_dir = args.from_dir
    iconIndex = input(
        '请输入新包名对应的数字：1->WhatsApp", "2->WhatsApp_GB",\n"'
        '3->WhatsApp_New","4->WhatsApp_2023","5->其他图标"\n')
    if iconIndex.strip() == "5":
        iconName = input('请输入新包名：\n')
        iconNameList.append(iconName)
    configPath = f'{from_dir[0:from_dir.rindex("/DecodeCode")]}/vestConfig'
    replaceIcon(f"{configPath}/{iconNameList[int(iconIndex) - 1]}", from_dir, configPath)
