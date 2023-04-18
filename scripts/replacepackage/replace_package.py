import argparse
import codecs
import glob
import os
import xml.etree.ElementTree as ET

# 替换的键值对，一行两个字符串，前面的是旧字符串，后面的是新字符串，中间用空格隔开
config_folderPath = 'scripts/replacepackage/properties'
vest_folderPath = 'scripts/replacepackage/vest'
# 只匹配下面的文件类型
extends = ["smali", "xml", "html"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF', 'original', 'apktool.yml']
# 默认包名集合列表
default_package_list = ["com.gbwhatsapp", "com.obwhatsapp", "com.WhatsApp2Plus",
                        "com.yowhatsapp", "com.whatsapp", "com.universe.messenger"]
# 新包名集合列表
new_package_list = default_package_list.copy()
# 用来保存properties配置的集合
mapping_string = {}
"""
    主要作用：反编译实现马甲包功能；替换默认包名为新包名。
"""


# 加载replacekeys.properties配置文件
def load_replace_keys(file_path, map_string):
    # 读取 properties 文件
    with codecs.open(file_path, "r", "utf-8") as rfile:
        for line in rfile.readlines():
            # 去掉行首行尾空格和换行符
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith('#'):
                continue
            if line.__contains__(r"\uD83C\uDFB5"):
                line = line.replace(r"\uD83C\uDFB5", "🎵")
                if line.find('🎵') > 0:
                    strs = line.split('🎵')
                    map_string[strs[0].strip()] = strs[1].strip()


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
def rename_directory(oldFolderName, newFolderName):
    curPath = os.getcwd()
    pos = curPath.rfind(r"smali")
    from_dir = curPath[:pos]
    # print(f"from_dir = {from_dir}")
    os.chdir(curPath)
    fileList = glob.glob(from_dir + "/" + "smali*/com/*")
    # print(fileList)
    for fpath in fileList:
        if fpath.rfind("/") > 0:
            dirName = fpath[fpath.rindex("/") + 1:]
            # print(f"dirName = {dirName}")
            if dirName == oldFolderName:
                relativePath = fpath.split(from_dir)[1]
                newDir = os.path.join(from_dir, relativePath.replace(oldFolderName, newFolderName))
                os.rename(fpath, newDir)


# 获取App名称
def getAppName(project_dir):
    stringPath = f"{project_dir}/res/values/strings.xml"
    parser = ET.parse(stringPath)
    root = parser.getroot()
    for child in root:
        attrib = child.attrib
        attrName = attrib.get("name")
        if not attrName is None and attrName == "yoShareSbj":
            return child.text


def getPropertiesName(folder_path, fpath):
    appList = ["GBWhatsApp", "OBWhatsApp", "WhatsAppPlus"]
    appName = getAppName(folder_path)
    match appList.index(appName):
        case 0:
            return f"{fpath}/gb_messenger.properties"
        case 1:
            return f"{fpath}/ob_messenger.properties"
        case 2:
            return f"{fpath}/plus_messenger.properties"


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path")
    args = parser.parse_args()
    folder_path = args.folder_path

    default_package = input(
        '请输入默认包名对应的数字：1->com.gbwhatsapp", "2->com.obwhatsapp","3->com.WhatsApp2Plus",\n'
        ' "4->com.yowhatsapp","5->com.whatsapp","6->com.universe.messenger","7->其他包名"\n')
    if default_package.strip() == "7":
        user_default_package = input('请输入默认包名：\n')
        default_package_list.append(user_default_package.strip())

    new_package = input(
        '请输入新包名对应的数字：1->com.gbwhatsapp", "2->com.obwhatsapp","3->com.WhatsApp2Plus",\n'
        ' "4->com.yowhatsapp","5->com.whatsapp","6->com.universe.messenger","7->其他包名"\n')
    if new_package.strip() == "7":
        user_new_package = input('请输入新包名：\n')
        new_package_list.append(user_new_package.strip())

    default_index = int(default_package) - 1
    new_index = int(new_package) - 1
    # 替换AndroidManifest
    # if new_index in range(0, 4):
    #     replace_manifest.replace_manifest(folder_path + "/AndroidManifest.xml",
    #                                       default_package_list[default_index],
    #                                       new_package_list[new_index])
    # 替换包名
    config_Path = f"{config_folderPath}/{new_package_list[new_index].split('.')[-1]}.properties"
    if new_index == 5:
        config_Path = getPropertiesName(folder_path, vest_folderPath)
    if not os.path.exists(config_Path):
        config_Path = f"{config_folderPath}/gbwhatsapp.properties"
    load_replace_keys(config_Path, mapping_string)
    execute_path(folder_path, blacklist, extends, mapping_string)
    # rename_directory(default_package_list[default_index].split(".")[-1],
    #                  new_package_list[new_index].split(".")[-1])
    print(f"执行完毕，输出结果保存到{folder_path}")
