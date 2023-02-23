import argparse
import codecs
import glob
import os
import shutil

# 只匹配下面的文件类型
extends = ["smali", "xml", "html"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF', 'original', 'apktool.yml']
# 默认包名集合列表
default_package_list = ["com.gbwhatsapp", "com.nouncebeats.otavia", "com.universe.messenger"]
# 新包名集合列表
new_package_list = default_package_list.copy()

"""
    主要作用：反编译实现马甲包功能；替换默认包名为新包名。
"""


# 加载replacekeys.properties配置文件
def load_replace_keys(defaultPackage, newPackage):
    oldClass = "L" + defaultPackage.replace(".", "/")
    newClass = "L" + newPackage.replace(".", "/")
    map_string = [(defaultPackage, newPackage),
                  (oldClass, newClass)]
    print(map_string)
    return map_string


def execute_path(folder_path, black_list, extends):
    os.chdir(folder_path)
    cwd = os.getcwd()
    dirs = os.listdir(cwd)
    for tmp in dirs:
        # 排除blacklist文件夹
        if tmp not in black_list:
            fpath = os.path.join(cwd, tmp)
            if os.path.isfile(fpath):
                print('fpath=', fpath)
                # 只extends的文件类型
                if fpath.split('.')[-1] in extends:
                    with codecs.open(fpath, "r", "utf-8") as rfile:
                        data = rfile.read()
                    with codecs.open(fpath, "w", "utf-8") as wfile:
                        replace_times = 0
                        for item in mapping_string:
                            replace_times += data.count(item[0])
                            data = data.replace(item[0], item[1])
                        print(r'替换次数：', replace_times)
                        wfile.write(data)
            # 如果是文件夹，递归
            elif os.path.isdir(fpath):
                execute_path(fpath, blacklist, extends)


# 重命名目录
def rename_directory(from_dir, oldFolderName, newFolderName):
    oldFolderName = oldFolderName.replace(".", "/")
    newFolderName = newFolderName.replace(".", "/")
    # print(f"oldFolderName = {oldFolderName} newFolderName = {newFolderName}")
    fileList = glob.glob(f"{from_dir}/**/com/{oldFolderName}/**")
    for fpath in fileList:
        relativePath = fpath.split(from_dir)[1]
        targetFolderPath = relativePath.replace(oldFolderName, newFolderName)
        targetPath = f"{from_dir}/{targetFolderPath}"
        newFolder = os.path.dirname(targetPath)
        if not os.path.exists(newFolder):
            os.makedirs(newFolder, exist_ok=True)
        shutil.move(fpath, targetPath)
    # 删除旧目录
    if oldFolderName != newFolderName:
        oldFolderName = oldFolderName.split("/")[0]
        folderList = glob.glob(f"{from_dir}/**/com/{oldFolderName}")
        for folderPath in folderList:
            removeDir(folderPath)


def removeDir(fromPath):
    listDir = os.listdir(fromPath)
    for fname in listDir:
        fpath = os.path.join(fromPath, fname)
        if os.path.isdir(fpath):
            shutil.rmtree(fpath,ignore_errors=True)
    os.rmdir(fromPath)


def getFolderName(packageName):
    nameList = packageName.split(".")
    defaultName = nameList[-1]
    if len(nameList) > 2:
        defaultName = packageName[len(nameList[0]) + 1:]
    return defaultName


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path")
    args = parser.parse_args()
    folder_path = args.folder_path

    default_package = input(
        '请输入默认包名对应的数字：1->com.gbwhatsapp", "2->com.nouncebeats.otavia",'
        ' "3->com.universe.messenger","4->其他包名"\n')
    if default_package.strip() == "4":
        user_default_package = input('请输入默认包名：\n')
        default_package_list.append(user_default_package.strip())

    new_package = input(
        '请输入默认包名对应的数字：1->com.gbwhatsapp", "2->com.nouncebeats.otavia",'
        ' "3->com.universe.messenger","4->其他包名"\n')
    if new_package.strip() == "4":
        user_new_package = input('请输入新包名：\n')
        new_package_list.append(user_new_package.strip())

    default_index = int(default_package) - 1
    new_index = int(new_package) - 1
    # 替换包名
    defaultPackage = default_package_list[default_index]
    newPackage = new_package_list[new_index]
    mapping_string = load_replace_keys(defaultPackage, newPackage)
    execute_path(folder_path, blacklist, extends)
    # 重命名文件夹
    oldPackage = getFolderName(defaultPackage)
    newPackage = getFolderName(newPackage)
    rename_directory(folder_path, oldPackage, newPackage)
    print(f"执行完毕，输出结果保存到{folder_path}")