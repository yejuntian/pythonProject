import codecs
import glob
import os
import re
import shutil
import time
import xml.etree.ElementTree as ET

# 默认文件夹名字
default_folder_name = "com/gbwhatsapp"
# 新包文件夹名字
new_folder_name = "com/whatsapp"
# 只匹配下面的文件类型
extends = ["smali", "xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'lib',
             'META-INF', 'original', 'apktool.yml']
# 项目地址
project_path = ""
# config.xml配置的路径列表集合
configPathList = ""
# 匹配smali*/后面的path地址。(eg:smali_classes5/android/support 输出结果为：android/support)
regex = r"/smali.*?/(.+)"
# 用于保存类对应关系集合
class_map = {}

"""
    主要作用：根据config.xml的配置；由gbwhatsapp包move到whatsapp包下，并矫正为WhatsApp路径。
"""


# gb目录转为wa目录
def convertWA(from_dir, mCurrentPath, isConsole=True):
    global project_path, configPathList
    project_path = from_dir
    before_time = time.time()
    for folderIndex in range(4, 7):
        moveFolder(project_path, folderIndex)
    if isConsole:
        configPathList = getConfigData(f"{mCurrentPath}/scripts/makeGBDiff/config.xml")
    else:
        configPathList = getConfigData(f"{mCurrentPath}/config.xml")
    convert_2_whatsapp()
    after_time = time.time()
    print(f"执行完毕，输出结果保存到：{project_path} 共耗时{after_time - before_time} 秒")


def moveFolder(project_path, folderIndex):
    # smali_classes4下的除了一级目录X目录，以外的其他目录或文件移动到smali目录下
    move_except_one_folder(f"{project_path}/smali_classes{folderIndex}", f"{project_path}/smali", "X")
    # 删除smali_classes4空文件夹目录
    deleteEmptyFolder(f"{project_path}/smali_classes{folderIndex}")


# 根据fpath路径，获取xml配置内容
def getConfigData(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    data_list = []
    for child in root:
        data_list.append(child.text)
    return data_list


def convert_2_whatsapp():
    # 遍历工程并移动文件
    traverseProjectAndMoveFile(project_path)
    correctWhatsFolderPath(project_path)


# 矫正项目中文件的路径
def correctWhatsFolderPath(project_path):
    fileList = glob.glob(f"{project_path}/smali*/com/whatsapp/**/*.smali", recursive=True)
    for fpath in fileList:
        fileRelativePath = getResultPath(fpath)
        # 矫正后的smali类路径和包名路径
        new_class_path = fileRelativePath.split(".smali")[0]
        new_smali_class_path = f"L{new_class_path}"
        new_package_class_path = new_class_path.replace("/", ".")
        # 矫正前后的smali类路径和包名路径
        old_class_path = new_class_path.replace(new_folder_name, default_folder_name)
        old_smali_class_path = f"L{old_class_path}"
        old_package_class_path = old_class_path.replace("/", ".")
        # 类对应关系保存到字典中
        class_map[old_smali_class_path] = new_smali_class_path
        class_map[old_package_class_path] = new_package_class_path
    # 遍历整个项目，并矫正smali类和xml路径
    traverseProjectCorrectPath(project_path, class_map)


def traverseProjectCorrectPath(from_dir, class_map):
    listdir = os.listdir(from_dir)
    for filename in listdir:
        fpath = os.path.join(from_dir, filename)
        if filename not in blacklist:
            if os.path.isdir(fpath):
                traverseProjectCorrectPath(fpath, class_map)
            elif os.path.isfile(fpath):
                # 只extends的文件类型
                if fpath.split('.')[-1] in extends:
                    print('fpath=', fpath)
                    # 保持AndroidManifest.xml原有xml格式需要单独处理
                    if filename == "AndroidManifest.xml":
                        save_2_xml(fpath, class_map)
                    else:
                        save_2_file(fpath, class_map)


# 保存到xml文件中
def save_2_xml(fpath, package_map_data):
    ET.register_namespace('android', "http://schemas.android.com/apk/res/android")
    parse = ET.parse(fpath)
    data = ET.tostring(parse.getroot(), encoding="utf-8").decode('utf-8').replace(' />', '/>')
    data = f'<?xml version="1.0" encoding="utf-8" standalone="no"?>{data}'
    with codecs.open(fpath, "w", "utf-8") as wfile:
        replace_times = 0
        for key, value in package_map_data.items():
            replace_times += data.count(key)
            data = data.replace(key, value)
        print(r'替换次数：', replace_times)
        wfile.write(data)


# 保存到文件中
def save_2_file(fpath, package_map_data):
    with codecs.open(fpath, "r", "utf-8") as rfile:
        data = rfile.read()
    with codecs.open(fpath, "w", "utf-8") as wfile:
        replace_times = 0
        for key, value in package_map_data.items():
            replace_times += data.count(key)
            data = data.replace(key, value)
        print(r'替换次数：', replace_times)
        wfile.write(data)


# 遍历from_dir并移动文件
def traverseProjectAndMoveFile(from_dir):
    listdir = os.listdir(from_dir)
    for fName in listdir:
        fpath = os.path.join(from_dir, fName)
        # 仅遍历smali文件
        if "smali" in fpath:
            if os.path.isdir(fpath):
                # smali文件的相对路径
                fileRelativePath = getResultPath(fpath)
                if fileRelativePath in configPathList:
                    # 移动qsmali文件到该目录下的WhatsApp文件夹下
                    destinationFolder = fpath.replace(default_folder_name, new_folder_name)
                    shutil.move(fpath, destinationFolder)
                else:
                    traverseProjectAndMoveFile(fpath)
            elif os.path.isfile(fpath):
                # smali文件的相对路径
                fileRelativePath = getResultPath(fpath)
                if fileRelativePath in configPathList:
                    targetFolder = from_dir.replace(default_folder_name, new_folder_name)
                    if not os.path.exists(targetFolder):
                        os.makedirs(targetFolder, exist_ok=True)
                    # 移动smali文件到该目录下的WhatsApp文件夹下
                    destinationFolder = fpath.replace(default_folder_name, new_folder_name)
                    shutil.move(fpath, destinationFolder)


# 获取文件夹smali*/后面的path相对地址
def getResultPath(from_path):
    matches = re.finditer(regex, from_path, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        return match.group(1)


def deleteEmptyFolder(source_folder):
    for root, dirs, files in os.walk(source_folder, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # 如果文件夹为空
                os.rmdir(dir_path)  # 删除空文件夹


# source_folder目录下除了excluded_folder以外的其他目录或文件移动到destination_folder目录
def move_except_one_folder(source_folder, destination_folder, excluded_folder):
    subItems = os.listdir(source_folder)
    for subItem in subItems:
        source_path = os.path.join(source_folder, subItem)
        if os.path.isdir(source_path) and subItem != excluded_folder:
            destination_path = os.path.join(destination_folder, subItem)
            if os.path.exists(destination_path):
                move_except_one_folder(source_path, destination_path, excluded_folder)
            else:
                shutil.move(source_path, destination_path)
        elif os.path.isfile(source_path):
            destination_path = os.path.join(destination_folder, subItem)
            shutil.move(source_path, destination_path)


if __name__ == "__main__":
    mCurrentPath = os.getcwd()
    from_dir = "/Users/shareit/work/shareit/gbdiff_2.24.2.76/DecodeCode/Whatsapp_v2.24.2.76"
    convertWA(from_dir, mCurrentPath, isConsole=False)
