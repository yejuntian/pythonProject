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
# 需要move到smali的文件夹列表
smali_folder_list = []
# 需要move到smali_classes2的文件夹列表
smali_classes2_folder_list = []


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
    to_file_path = from_file_path.replace(default_folder_name, "whatsapp")

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
        to_file_path = fpath.replace(default_folder_name, "whatsapp")
        print(f"fpath = {fpath} newfilePath = {to_file_path}")
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


def convert_2_whatsapp():
    traverse_folder(dir_path)
    # 移动到smali目录
    for smali_folder in smali_folder_list:
        moveFile_2_target_folder(smali_folder, True)
    # 移动到smali_classes2目录
    for smali_folder in smali_classes2_folder_list:
        moveFile_2_target_folder(smali_folder, False)


if __name__ == "__main__":
    # smali_1_folder_list = get_dir_list("script/gbwhatsapp_2_whatsapp/smali.xml")
    smali_1_folder_list = get_data_list("smali.xml")
    # smali_2_folder_list = get_dir_list("script/gbwhatsapp_2_whatsapp/smali_classes2.xml")
    smali_2_folder_list = get_data_list("smali_classes2.xml")
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.18.71"
    dir_path = from_dir
    convert_2_whatsapp()
