import codecs
import glob
import os
import re
import time
import xml.etree.ElementTree as ET

# 只匹配下面的文件类型
extends = ["smali", "xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'lib',
             'META-INF', 'original', 'apktool.yml',
             'smali_classes6', 'smali_classes7', 'smali_classes8',
             'smali_classes9', 'smali_classes10', 'smali_classes11',
             'smali_classes12', 'smali_classes13', 'smali_classes14']
# 用于保存类对应关系集合
data_map = {}
# 匹配smali*/后面的path地址。(eg:smali_classes5/android/support 输出结果为：android/support)
regex = r"/smali.*?/(.+)"
# 排除路径集合
excludePathList = []
# 使用旧命名方式(多个版本确认新命名方式没问题后,废弃旧命名方式)
isUseOldStyle = True

"""
    主要作用：读取renameFolder/config.xml配置文件，重命名文件夹名。
"""


def changeFolder(from_dir, mCurrentPath, isConsole=True):
    if isConsole:
        configPathList = getConfigData(f"{mCurrentPath}/config.xml")
    else:
        configPathList = getConfigData(f"{mCurrentPath}/myproject/renameFolder/config.xml")
    for configPath in configPathList:
        file_list = glob.glob(f"{from_dir}/{configPath}/**/*.smali", recursive=True)
        for file_path in file_list:
            # 排除路径
            if isExcludePath(file_path):
                continue
            from_file_path = file_path
            to_file_path = file_path.replace(".smali", "2.smali")
            # 设置类名的对应关系
            set_data_map(from_file_path, to_file_path)
    print(data_map)


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
    if isUseOldStyle:
        # 原来路径和新路径的对应关系
        data_map[f"{old_class_path1};"] = f"{new_class_path1};"
        """
        重命名会有问题，应该保持重命名前的才对

        例如：
        类名Lcom/google/android/gms/auth2/api/signin/RevocationBoundService;
        重命名前：const-string v0, "com.google.android.gms.auth.api.signin.RevocationBoundService.disconnect"
        重命名后：const-string v0, "com.google.android.gms.auth2.api.signin.RevocationBoundService.disconnect"
        """
        data_map[old_class_path2] = new_class_path2
    else:
        # 原来路径和新路径的对应关系
        # smali类对应路径eg:Landroidx/appcompat/view/menu/ActionMenuItemView;
        data_map[f"L{old_class_path1};"] = f"L{new_class_path1};"
        # smali类和AndroidManifest.xml对应路径eg:"androidx.appcompat.view.menu.ActionMenuItemView"
        data_map[f'"{old_class_path2}"'] = f'"{new_class_path2}"'
        # xml类对应路径
        # eg:<androidy.appcompat.widget.Toolbar
        data_map[f'<{old_class_path2} '] = f'<{new_class_path2} '
        # eg:</androidy.appcompat.widget.Toolbar
        data_map[f'</{old_class_path2}'] = f'</{new_class_path2}'
        # kotlin类对应路径eg:\nkotlin/collections/CollectionsKt___CollectionsKt2\n
        data_map[f"\\n{old_class_path1}\\n"] = f"\\n{new_class_path1}\\n"


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


def renameSmaliFile(from_dir, mCurrentPath, isConsole=True):
    if isConsole:
        configPathList = getConfigData(f"{mCurrentPath}/config.xml")
    else:
        configPathList = getConfigData(f"{mCurrentPath}/myproject/renameFolder/config.xml")
    for folderPath in configPathList:
        rename_smali_files(f"{from_dir}/{folderPath}")


def rename_smali_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".smali"):
                old_file_path = os.path.join(root, file)
                # 获取不包含后缀的文件名
                base_name = file[:-6]  # 去掉 .smali 后缀
                new_file_path = os.path.join(root, f"{base_name}2.smali")

                # 排除路径
                if isExcludePath(old_file_path):
                    continue
                # Rename the file
                os.rename(old_file_path, new_file_path)
                # print(f"Renamed {old_file_path} to {new_file_path}")


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


def renameFolder(from_dir):
    before_time = time.time()
    mCurrentPath = os.getcwd()
    changeFolder(from_dir, mCurrentPath, isConsole=True)
    traverse_folder(from_dir, data_map)
    renameSmaliFile(from_dir, mCurrentPath, isConsole=True)
    after_time = time.time()
    print(f"执行完毕，输出结果保存到：{from_dir} 共耗时{after_time - before_time} 秒")


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/Snaptube_v72050310/DecodeCode/Snaptube_v72050310"
    renameFolder(from_dir)
