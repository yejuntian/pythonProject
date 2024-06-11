import codecs
import glob
import os
import re
import shutil
import time
import xml.etree.ElementTree as ET

# 只匹配下面的文件类型
extends = ["smali", "xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'lib',
             'META-INF', 'original', 'apktool.yml',
             'smali_classes6','smali_classes7','smali_classes8','smali_classes9']
# 用于保存类对应关系集合
data_map = {}
# 匹配smali*/后面的path地址。(eg:smali_classes5/android/support 输出结果为：android/support)
regex = r"/smali.*?/(.+)"
# 排除路径集合
excludePathList = ["com/google/android/exoplayer2/ext",
                   "com/google/android/exoplayer2/decoder"]

"""
    主要作用：读取rename_google/config.xml配置文件，重命名config.xml配置路径的文件夹名。
"""


# 由support目录 变为 supporty,并设置类名的对应关系
def change_googleFolder(from_dir, mCurrentPath, isConsole=True):
    if isConsole:
        configPathList = getConfigData(f"{mCurrentPath}/config.xml")
    else:
        configPathList = getConfigData(f"{mCurrentPath}/gbwhatsapp/rename_google/config.xml")
    for configPath in configPathList:
        file_list = glob.glob(f"{from_dir}/smali*/{configPath}/**/*.smali", recursive=True)
        for file_path in file_list:
            # 排除路径
            if isExcludePath(file_path):
                continue
            from_file_path = file_path
            to_file_path = file_path.replace(configPath, f"{configPath}2")
            file_dir = os.path.dirname(to_file_path)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir, exist_ok=True)
            shutil.move(file_path, to_file_path)
            # 设置类名的对应关系
            set_data_map(from_file_path, to_file_path)
    # print(data_map)


# 是否为排除的目录
def isExcludePath(file_path):
    for fpath in excludePathList:
        if file_path.__contains__(fpath):
            return True
    return False


# 根据fpath路径，获取xml配置内容
def getConfigData(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    data_list = []
    for child in root:
        data_list.append(child.text)
    return data_list


# 设置类名的对应关系
def set_data_map(from_file_path, to_file_path):
    # 原来路径
    oldPathList = getResultPath(from_file_path)
    old_class_path1 = oldPathList[0]
    old_class_path2 = oldPathList[1]
    # 新路径
    newPathList = getResultPath(to_file_path)
    new_class_path1 = newPathList[0]
    new_class_path2 = newPathList[1]
    # 原来路径和新路径的对应关系
    data_map[f"{old_class_path1};"] = f"{new_class_path1};"
    data_map[old_class_path2] = new_class_path2


# 获取文件夹smali*/后面的path相对地址
def getResultPath(from_file_path):
    matches = re.finditer(regex, from_file_path, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        from_path1 = match.group(1).split(".smali")[0]
        from_path2 = from_path1.replace("/", ".")
        return from_path1, from_path2


# 遍历文件，替换为data_map中的字符串
def traverse_folder(from_dir, data_map):
    listdir = os.listdir(from_dir)
    for filename in listdir:
        file_path = os.path.join(from_dir, filename)
        print(file_path)
        if filename not in blacklist:
            if os.path.isdir(file_path):
                traverse_folder(file_path, data_map)
            elif os.path.isfile(file_path):
                if file_path.split(".")[-1] in extends:
                    save_2_file(file_path, data_map)


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


def convertGoogleFolder(from_dir):
    before_time = time.time()
    mCurrentPath = os.getcwd()
    change_googleFolder(from_dir, mCurrentPath, isConsole=True)
    traverse_folder(from_dir, data_map)
    after_time = time.time()
    print(f"执行完毕，输出结果保存到：{from_dir} 共耗时{after_time - before_time} 秒")


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/GBWorke/Snaptube_v72050310/DecodeCode/Snaptube_v72050310"
    convertGoogleFolder(from_dir)
