import codecs
import glob
import os
import shutil
import xml.etree.ElementTree as ET

dir_path = ""
# 需要移动到smali目录的文件列表
smali_1_folder_list = []
# 需要move到smali_classes2的目录列表
smali_2_folder_list = []
# 默认文件夹名字
default_folder_name = "gbwhatsapp"
# 新包文件夹名字
new_folder_name = "whatsapp"
# 需要move到smali的文件夹列表
smali_folder_list = []
# 需要move到smali_classes2的文件夹列表
smali_classes2_folder_list = []
# 只匹配下面的文件类型
extends = ["smali", "xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin',
             'lib', 'META-INF', 'original', 'apktool.yml']


# 获取目录列表
def get_data_list(path):
    parse = ET.parse(path)
    root = parse.getroot()
    data_list = []
    for child in root:
        data_list.append(child.text)
    return data_list


# 获取矫正的路径path
def get_correct_path(old_path, folder):
    file_dir = old_path[len(dir_path) + 1:]
    correct_path = f'{dir_path}/{folder}{file_dir[file_dir.index("/"):]}'
    return correct_path


# move 文件
def start_move_file(fileName, from_file_path, isFile):
    is_move_file = False
    to_file_path = from_file_path.replace(default_folder_name, new_folder_name)

    if fileName in smali_1_folder_list:
        to_file_path = get_correct_path(to_file_path, "smali")
        create_folder(from_file_path, to_file_path)
        if isFile:
            if os.path.exists(from_file_path):
                shutil.move(from_file_path, to_file_path)
        else:
            # print(to_file_path)
            smali_folder_list.append(from_file_path)
        is_move_file = True
    elif fileName in smali_2_folder_list:
        to_file_path = get_correct_path(to_file_path, "smali_classes2")
        create_folder(from_file_path, to_file_path)
        if isFile:
            if os.path.exists(from_file_path):
                shutil.move(from_file_path, to_file_path)
        else:
            # print(to_file_path)
            smali_classes2_folder_list.append(from_file_path)
        is_move_file = True
    return is_move_file


# 创建文件夹
def create_folder(from_file_path, to_file_path):
    if os.path.isdir(from_file_path):
        if not os.path.exists(to_file_path):
            os.makedirs(to_file_path, exist_ok=True)
    elif os.path.isfile(from_file_path):
        folder = os.path.dirname(to_file_path)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)


# 递归遍历文件夹，移动后缀为.smali的文件
def traverse_folder(from_dir):
    listdir = os.listdir(from_dir)
    for fileName in listdir:
        from_file_path = str(os.path.join(from_dir, fileName))
        # 是否move文件的标识
        is_move_file = False
        # 过滤其他文件，仅遍历smali文件夹
        if from_file_path.__contains__("smali"):
            if os.path.isdir(from_file_path):
                if from_file_path.__contains__(default_folder_name):
                    fileName = default_folder_name + from_file_path.split(default_folder_name)[1]

                    # move文件到smali对应目录
                    is_move_file = start_move_file(fileName, from_file_path, False)
                if is_move_file:
                    continue
                else:
                    # 继续递归遍历文件夹
                    traverse_folder(from_file_path)
            elif os.path.isfile(from_file_path):  # 移动文件
                if from_file_path.__contains__(default_folder_name):
                    fileName = default_folder_name + from_file_path.split(default_folder_name)[1]
                    # move文件到smali对应目录
                    start_move_file(fileName, from_file_path, True)
        else:  # 其他文件
            continue


# 移动文件到指定目录
def moveFile_2_target_folder(file_path, isMoveSmaliFolder):
    """
       file_path:文件夹路径
       isMoveSmaliFolder：是否移动到smali目录
    """
    listdir = os.listdir(file_path)
    for fileName in listdir:
        fpath = str(os.path.join(file_path, fileName))
        to_file_path = fpath.replace(default_folder_name, new_folder_name)
        # print(f"fpath = {fpath} newfilePath = {to_file_path}")
        if os.path.isdir(fpath):
            moveFile_2_target_folder(fpath, isMoveSmaliFolder)
            pass
        elif os.path.isfile(fpath):
            if isMoveSmaliFolder:
                to_file_path = get_correct_path(to_file_path, "smali")
                create_folder(fpath, to_file_path)
                shutil.move(fpath, to_file_path)
            else:
                to_file_path = get_correct_path(to_file_path, "smali_classes2")
                create_folder(fpath, to_file_path)
                shutil.move(fpath, to_file_path)


# 获取旧包名和新包名的对应关系，并保存到map中
def get_package_map(package):
    data_map = {}
    # 新包名
    new_package1 = package[0:package.rindex(".")]
    new_package2 = new_package1.replace("/", ".")
    # 旧包名
    old_package1 = new_package1.replace(new_folder_name, default_folder_name)
    old_package2 = new_package2.replace(new_folder_name, default_folder_name)

    data_map[f"L{old_package1}"] = f"L{new_package1}"
    data_map[old_package2] = new_package2
    # print(data_map)
    return data_map


# 遍历WhatsApp目录的所有文件，替换为新包名
def replace_package():
    filelist = glob.glob(f"{from_dir}/smali*/com/{new_folder_name}/**/*.smali", recursive=True)
    for file_path in filelist:
        temp_str = f"{from_dir}/smali_classes2"
        if file_path.__contains__(temp_str):
            package = file_path[len(temp_str) + 1:]
            package_map = get_package_map(package)
            # print(package_map)
            # 遍历每个文件替换包名
            traverse_folder_replace_package(from_dir, package_map)
        else:
            package = file_path[len(f"{from_dir}/smali") + 1:]
            package_map = get_package_map(package)
            # print(package_map)
            # 遍历每个文件替换包名
            traverse_folder_replace_package(from_dir, package_map)


# 遍历每个文件替换包名
def traverse_folder_replace_package(file_path, package_map_data):
    listdir = os.listdir(file_path)
    for filename in listdir:
        fpath = str(os.path.join(file_path, filename))
        if filename not in blacklist:
            if os.path.isdir(fpath):
                traverse_folder_replace_package(fpath, package_map_data)
            elif os.path.isfile(fpath):
                # 只extends的文件类型
                if fpath.split('.')[-1] in extends:
                    print('fpath=', fpath)
                    with codecs.open(fpath, "r", "utf-8") as rfile:
                        data = rfile.read()
                    with codecs.open(fpath, "w", "utf-8") as wfile:
                        replace_times = 0
                        for key, value in package_map_data.items():
                            replace_times += data.count(key)
                            data = data.replace(key, value)
                        print(r'替换次数：', replace_times)
                        wfile.write(data)


def convert_2_whatsapp():
    traverse_folder(dir_path)
    # 移动到smali目录
    for smali_folder in smali_folder_list:
        moveFile_2_target_folder(smali_folder, True)
    # 移动到smali_classes2目录
    for smali_folder in smali_classes2_folder_list:
        moveFile_2_target_folder(smali_folder, False)
    # 替换包名
    replace_package()


if __name__ == "__main__":
    # smali_1_folder_list = get_dir_list("script/gbwhatsapp_2_whatsapp/smali.xml")
    smali_1_folder_list = get_data_list("smali.xml")
    # smali_2_folder_list = get_dir_list("script/gbwhatsapp_2_whatsapp/smali_classes2.xml")
    smali_2_folder_list = get_data_list("smali_classes2.xml")
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.18.71"
    dir_path = from_dir
    convert_2_whatsapp()
