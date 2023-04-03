import argparse
import codecs
import glob
import os
import shutil
from replace_icon import replaceIcon

# 只匹配下面的文件类型
extends = ["smali", "xml", "html"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF', 'original', 'apktool.yml']
# 默认包名集合列表
default_package_list = ["com.gbwhatsapp", "com.nouncebeats.otavia", "com.universe.messenger",
                        "com.obwhatsapp", "com.WhatsApp2Plus", "com.yowhatsapp", "com.whatsapp"]
# 产品名
productNameList = ["agb", "aob", "aplus", "bgb", "bob", "bplus"]
# flurry注册key
flurryList = ["VCW5NHMZV2ZK48YXYFKN", "QBBWBTZS28DR73H3CMDT", "RDRKVWX8XXHMCY78RCDQ"]
# 新包名集合列表
new_package_list = default_package_list.copy()

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


# 替换产品名
def startReplaceProductName(index, propertiesPath, configPath, to_dir, mapping_string):
    dict = {0: "gb", 3: "ob", 4: "plus", 5: "yo"}
    productNameList = ["agb", "aob", "aplus", "bgb", "bob", "bplus"]
    if index in range(1, 3):
        productIndex = input(f'请输入产品名对应的数字：1->agb;2->aob;3->aplus;4->bgb;5->bob;6->bplus\n')
        if productIndex.isnumeric() and int(productIndex) in range(1, 7):
            pos = int(productIndex) - 1
            # 替换otavia/message兜底升级key
            replaceProductName(to_dir, productNameList[pos])
            replaceFlurryKey(mapping_string, pos)
            # 替换新Icon
            replaceIcon(f"{configPath}/{productNameList[pos]}", to_dir, configPath)
    elif index in dict.keys():
        # 替换gb/ob/plus/yo兜底升级key
        replaceProductName(to_dir, dict[index])
    # 读取配置文件
    loadData(propertiesPath, mapping_string)


# 加载配置文件
def loadData(file_path, mapping_string):
    print(file_path)
    if not os.path.exists(file_path):
        return
    with codecs.open(file_path, "r", "utf-8") as rfile:
        for line in rfile.readlines():
            line = line.strip()
            if not line.__contains__("#"):
                if line.find('=') > 0:
                    strs = line.split("=")
                    mapping_string[strs[0].strip()] = strs[1].strip()


# 替换flurry注册key
def replaceFlurryKey(mapping_string, pos):
    if pos < len(flurryList):
        mapping_string["B5K3D7FRBWN8NV8JS8HT"] = flurryList[pos]


# 替换兜底升级配置
def replaceProductName(from_dir, productName):
    filePathList = glob.glob(f"{from_dir}/smali**/**/**/ProductConfig.smali")
    if len(filePathList) > 0:
        fpath = filePathList[0]
        str = '.field private static PRODUCT_SHORT_NAME:Ljava/lang/String; = '
        with codecs.open(fpath, "r", "utf-8") as rf:
            lines = rf.readlines()
        with codecs.open(fpath, "w", "utf-8") as wf:
            result = ""
            for line in lines:
                if line.startswith(str):
                    line = f'{str}"{productName}"\n'
                result += line
            wf.write(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path")
    args = parser.parse_args()
    folder_path = args.folder_path

    default_package = input(
        '请输入默认包名对应的数字：1->com.gbwhatsapp", "2->com.nouncebeats.otavia",'
        ' "3->com.universe.messenger",\n"4->com.obwhatsapp", "5->com.WhatsApp2Plus", '
        '"6->com.yowhatsapp", "7->com.whatsapp""8->其他包名"\n')
    if default_package.strip() == "8":
        user_default_package = input('请输入默认包名：\n')
        default_package_list.append(user_default_package.strip())

    new_package = input(
        '请输入新包名对应的数字：1->com.gbwhatsapp", "2->com.nouncebeats.otavia",'
        ' "3->com.universe.messenger",\n"4->com.obwhatsapp", "5->com.WhatsApp2Plus", '
        '"6->com.yowhatsapp", "7->com.whatsapp""8->其他包名"\n')
    if new_package.strip() == "8":
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
    propertiesPath = f'{vestConfigPath}/{newPackage.split(".")[-1]}.properties'
    startReplaceProductName(new_index, propertiesPath, vestConfigPath, folder_path, mapping_string)
    # 只有包名不同，才替换包名
    if new_index != default_index:
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
