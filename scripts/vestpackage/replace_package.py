import argparse
import codecs
import glob
import os
import xml.etree.ElementTree as ET
import shutil

# 只匹配下面的文件类型
extends = ["smali", "xml", "html"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF', 'original', 'apktool.yml']
# 默认包名集合列表
default_package_list = ["com.gbwhatsapp", "com.bello", "com.universe.messenger",
                        "com.obwhatsapp", "com.WhatsApp2Plus", "com.whatsapp"]
# 新包名集合列表
new_package_list = default_package_list.copy()
appList = ["GBWhatsApp", "OBWhatsApp", "WhatsAppPlus"]
"""
    主要作用：反编译实现马甲包功能；替换默认包名为新包名。
"""


# 加载replacekeys.properties配置文件
def load_replace_keys(defaultPackage, newPackage):
    oldClass = "L" + defaultPackage.replace(".", "/")
    newClass = "L" + newPackage.replace(".", "/")
    map_string = {defaultPackage: newPackage, oldClass: newClass}
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
                        for key, value in mapping_string.items():
                            replace_times += data.count(key)
                            data = data.replace(key, value)
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
            deleteEmptyFolder(folderPath)


def deleteEmptyFolder(source_folder):
    for root, dirs, files in os.walk(source_folder, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # 如果文件夹为空
                os.rmdir(dir_path)  # 删除空文件夹


def getFolderName(packageName):
    nameList = packageName.split(".")
    defaultName = nameList[-1]
    if len(nameList) > 2:
        defaultName = packageName[len(nameList[0]) + 1:]
    return defaultName


def readConfigFile(newPackage, vestConfigPath, to_dir, mapping_string):
    productList = ["gb", "ob", "plus"]
    product_name = getProductName(to_dir)
    if product_name is not None:
        productIndex = appList.index(product_name)
        propertiesPath = f'{vestConfigPath}/{newPackage.split(".")[-1]}/{productList[productIndex]}.properties'
        loadData(propertiesPath, mapping_string)


# 获取兜底产品名称
def getProductName(project_dir):
    stringPath = f"{project_dir}/res/values-v1/strings.xml"
    if not os.path.exists(stringPath):
        return
    parser = ET.parse(stringPath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        if not attrName is None and attrName == "yoShareSbj":
            return child.text


# 加载配置文件
def loadData(file_path, mapping_string):
    print(file_path)
    if not os.path.exists(file_path):
        return
    with codecs.open(file_path, "r", "utf-8") as rfile:
        for line in rfile.readlines():
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith('#'):
                continue
            if line.__contains__(r"\uD83C\uDFB5"):
                line = line.replace(r"\uD83C\uDFB5", "🎵")
                if line.find('🎵') > 0:
                    strs = line.split("🎵")
                    mapping_string[strs[0].strip()] = strs[1].strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path")
    args = parser.parse_args()
    folder_path = args.folder_path

    default_package = input(
        '请输入默认包名对应的数字：\n"1->com.gbwhatsapp", "2->com.bello",'
        ' "3->com.universe.messenger",\n"4->com.obwhatsapp", "5->com.WhatsApp2Plus", '
        '"6->com.whatsapp","7->其他包名"\n')
    if default_package.strip() == "7":
        user_default_package = input('请输入默认包名：\n')
        default_package_list.append(user_default_package.strip())

    new_package = input(
        '请输入新包名对应的数字：\n"1->com.gbwhatsapp", "2->com.bello",'
        ' "3->com.universe.messenger",\n"4->com.obwhatsapp", "5->com.WhatsApp2Plus", '
        '"6->com.whatsapp","7->其他包名"\n')
    if new_package.strip() == "7":
        user_new_package = input('请输入新包名：\n')
        new_package_list.append(user_new_package.strip())

    default_index = int(default_package) - 1
    new_index = int(new_package) - 1
    # 包名
    defaultPackage = default_package_list[default_index]
    newPackage = new_package_list[new_index]
    mapping_string = load_replace_keys(defaultPackage, newPackage)
    # 替换产品名操作
    vestConfigPath = f'{folder_path[0:folder_path.rindex("/")]}/vestConfig'
    if folder_path.__contains__("/DecodeCode"):
        vestConfigPath = f'{folder_path[0:folder_path.rindex("/DecodeCode")]}/vestConfig'
    readConfigFile(newPackage, vestConfigPath, folder_path, mapping_string)
    # 只有包名不同，才替换包名
    if new_index != default_index or new_index == 6:
        execute_path(folder_path, blacklist, extends, mapping_string)
        # 重命名文件夹
        oldPackage = getFolderName(defaultPackage)
        newPackage = getFolderName(newPackage)
        rename_directory(folder_path, oldPackage, newPackage)
    else:
        print("******* 检测到包名一致，无需遍历替换包名 ********")
    print(f"执行完毕，输出结果保存到{folder_path}")


if __name__ == '__main__':
    main()
