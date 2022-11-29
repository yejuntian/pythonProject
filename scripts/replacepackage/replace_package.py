import argparse
import codecs
import glob
import os
import replace_manifest

# 替换的键值对，一行两个字符串，前面的是旧字符串，后面的是新字符串，中间用空格隔开
key_path = 'scripts/replacepackage/replacekeys.properties'
# 只匹配下面的文件类型
extends = ["smali", "xml", "html"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF',
             'original', 'AndroidManifest.xml', 'apktool.yml']
# 默认包名集合列表
default_package_list = ["com.gbwhatsapp", "com.obwhatsapp", "com.WhatsApp2Plus", "com.yowhatsapp"]
# 新包名集合列表
new_package_list = default_package_list.copy()

"""
    主要作用：反编译实现马甲包功能；替换默认包名为新包名。
"""


# 加载replacekeys.properties配置文件
def load_replace_keys(file_path):
    map_string = []
    with codecs.open(file_path, "r", "utf-8") as rfile:
        for line in rfile.readlines():
            line = line.strip()
            if not line.__contains__("#"):
                if line.find('=') > 0:
                    strs = line.split("=")
                    map_string.append([strs[0].strip(), strs[1].strip()])
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
def rename_directory(oldFolderName, newFolderName):
    curPath = os.getcwd()
    pos = curPath.rfind(r"smali")
    curPath = curPath[:pos]
    # print(f"curPath = {curPath}")
    os.chdir(curPath)
    fileList = glob.glob(curPath + "/" + "smali*/com/*")
    # print(fileList)
    for file in fileList:
        if file.rfind("/") > 0:
            dirName = file[file.rindex("/") + 1:]
            # print(f"dirName = {dirName}")
            if dirName == oldFolderName:
                newDir = file.replace(oldFolderName, newFolderName)
                os.rename(file, newDir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path")
    args = parser.parse_args()
    folder_path = args.folder_path

    default_package = input(
        '请输入默认包名对应的数字：1->com.gbwhatsapp", "2->com.obwhatsapp",'
        ' "3->com.WhatsApp2Plus", "4->com.yowhatsapp","5->其他包名"\n')
    if default_package.strip() == "5":
        user_default_package = input('请输入默认包名：\n')
        default_package_list.append(user_default_package.strip())

    new_package = input(
        '请输入新包名对应的数字：1->com.gbwhatsapp", "2->com.obwhatsapp",'
        ' "3->com.WhatsApp2Plus", "4->com.yowhatsapp","5->其他包名"\n')
    if new_package.strip() == "5":
        user_new_package = input('请输入新包名：\n')
        new_package_list.append(user_new_package.strip())

    default_index = int(default_package) - 1
    new_index = int(new_package) - 1
    # 替换AndroidManifest
    replace_manifest.replace_manifest(folder_path + "/AndroidManifest.xml",
                                      default_package_list[default_index],
                                      new_package_list[new_index])
    # 替换包名
    mapping_string = load_replace_keys(key_path)
    execute_path(folder_path, blacklist, extends)
    rename_directory(default_package_list[default_index].split(".")[-1],
                     new_package_list[new_index].split(".")[-1])
    print(f"执行完毕，输出结果保存到{folder_path}")
