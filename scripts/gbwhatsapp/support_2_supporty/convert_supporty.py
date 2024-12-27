import argparse
import codecs
import glob
import os
import re
import shutil
import time

# 只匹配下面的文件类型
extends = ["smali", "xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'lib',
             'META-INF', 'original', 'apktool.yml']
# 用于保存类对应关系集合
data_map = {}
# 匹配smali*/后面的path地址。(eg:smali_classes5/android/support 输出结果为：android/support)
regex = r"/smali.*?/(.+)"
# 使用旧命名方式(多个版本确认新命名方式没问题后,废弃旧命名方式)
isUseOldStyle = True
"""
    主要作用：support变为supporty
"""


# 由support目录 变为 supporty,并设置类名的对应关系
def change_support_2_supporty(from_dir):
    file_list = glob.glob(f"{from_dir}/smali*/android/support/**/*.smali", recursive=True)
    for file_path in file_list:
        from_file_path = file_path
        to_file_path = file_path.replace("android/support", "android/supporty")
        file_dir = os.path.dirname(to_file_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir, exist_ok=True)
        shutil.move(file_path, to_file_path)
        # 设置类名的对应关系
        set_data_map(from_file_path, to_file_path)


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
        data_map[f"L{old_class_path1};"] = f"L{new_class_path1};"
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
        file_path = str(os.path.join(from_dir, filename))
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


def convertSupportY(from_dir):
    before_time = time.time()
    change_support_2_supporty(from_dir)
    traverse_folder(from_dir, data_map)
    after_time = time.time()
    print(f"执行完毕，输出结果保存到：{from_dir} 共耗时{after_time - before_time} 秒")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    convertSupportY(args.from_dir)
