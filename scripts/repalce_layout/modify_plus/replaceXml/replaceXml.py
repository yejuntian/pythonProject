import os
import xml.etree.ElementTree as ET
import shutil
import argparse

"""
    主要作用：
    from_dir：需要删除文件的项目path
    to_dir：需要copy文件的项目path
    1.遍历目标目录并删除文件列表中的文件。
    2.从另一个项目目录中复制同名文件到删除后的文件位置。
"""


def loadFileList(fpath):
    parse = ET.parse(fpath)
    root = parse.getroot()
    layoutList = []
    for child in root:
        layoutName = child.text
        if not layoutName is None:
            layoutList.append(layoutName.strip())
    return layoutList


def delete_and_replace_files(target_directory, source_directory, file_list):
    """
    删除目标目录中的指定文件，并用源目录中的同名文件替换它们。

    参数:
    - target_directory (str): 要遍历并删除文件的目标目录路径。
    - source_directory (str): 从中复制文件的源目录路径。
    - file_list (list): 要删除并替换的文件名列表。

    返回:
    - failed_operations (list): 删除或替换失败的文件及其错误信息。
    """
    failed_operations = []

    for root, dirs, files in os.walk(target_directory):
        for file_name in files:
            if file_name in file_list:
                target_file_path = os.path.join(root, file_name)
                source_file_path = os.path.join(source_directory, file_name)

                # 删除目标文件
                try:
                    os.remove(target_file_path)
                    # print(f"Deleted: {target_file_path}")
                except Exception as e:
                    failed_operations.append((target_file_path, f"Failed to delete. Reason: {e}"))
                    continue

                # 复制源文件到目标位置
                if os.path.exists(source_file_path):
                    try:
                        shutil.copy2(source_file_path, target_file_path)
                        # print(f"Copied: {source_file_path} to {target_file_path}")
                    except Exception as e:
                        failed_operations.append((source_file_path, f"Failed to copy. Reason: {e}"))
                else:
                    failed_operations.append((source_file_path, "Source file does not exist."))

    return failed_operations


# 示例使用
if __name__ == "__main__":
    mCurrentPath = os.getcwd()
    parser = argparse.ArgumentParser()
    from_dir = parser.add_argument("from_dir")
    to_dir = parser.add_argument("to_dir")
    args = parser.parse_args()

    # from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.15.78/DecodeCode/Whatsapp_v2.24.15.78"
    # to_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.11.79/DecodeCode/Whatsapp_v2.24.11.79"
    files_to_replace = loadFileList(f"{mCurrentPath}/scripts/repalce_layout/modify_plus/replaceXml/config.xml")
    failed = delete_and_replace_files(f"{args.from_dir}/res/xml", f"{args.to_dir}/res/xml", files_to_replace)
    if failed:
        print("Failed operations:", failed)
    print("***************程序执行结束******************")
