import codecs
import glob
import os
import shutil

# 只匹配下面的文件类型
extends = ["smali", "xml", "html"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF', 'original', 'apktool.yml']

"""
    主要作用：替换包名com.whatsapp---》com.gbwhatsapp。
"""


# 加载replacekeys.properties配置文件
def load_replace_keys(defaultPackage, newPackage):
    oldClass = "L" + defaultPackage.replace(".", "/")
    newClass = "L" + newPackage.replace(".", "/")
    map_string = [(defaultPackage, newPackage),
                  (oldClass, newClass)]
    print(map_string)
    return map_string


def execute_path(folder_path, black_list, extends, mapping_string):
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
                execute_path(fpath, blacklist, extends, mapping_string)


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
            shutil.rmtree(fpath, ignore_errors=True)
    os.rmdir(fromPath)


def getFolderName(packageName):
    nameList = packageName.split(".")
    defaultName = nameList[-1]
    if len(nameList) > 2:
        defaultName = packageName[len(nameList[0]) + 1:]
    return defaultName


# 程序入口
def replacePackage(from_dir):
    folder_path = from_dir
    # 替换包名
    defaultPackage = "com.whatsapp"
    newPackage = "com.gbwhatsapp"
    mapping_string = load_replace_keys(defaultPackage, newPackage)
    execute_path(folder_path, blacklist, extends, mapping_string)
    # 重命名文件夹
    oldPackage = getFolderName(defaultPackage)
    newPackage = getFolderName(newPackage)
    rename_directory(folder_path, oldPackage, newPackage)
