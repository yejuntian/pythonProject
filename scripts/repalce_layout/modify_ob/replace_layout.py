import argparse
import os
import shutil

xmlList = ["allo_conversation_entry.xml", "conversation_entry.xml",
           "dribblev2_conversation_entry.xml", "theme_conversation_old_stock_entry.xml",
           "theme_conversation_stock_entry.xml", "theme_ios14_conversation_entry.xml",
           "theme_msggoogle_conversation_entry.xml", "theme_telegramxios_conversation_entry.xml"]

"""
 主要作用：读取ob_replaceStr文本内容，并替换ob_targetStr目标字符串。
"""


def replaceLayout(from_dir):
    for fname in xmlList:
        fName = fname.split(".")[0]
        folderPath = f"{mCurrentPath}/scripts/repalce_layout/modify_ob/{fName}"
        listdir = os.listdir(folderPath)
        suffix = ""
        if len(listdir) == 2:
            replaceXmlStr(from_dir, fName, fname, suffix)
        elif len(listdir) == 4:
            for index in range(1, 3):
                if index == 2:
                    suffix = "2"
                replaceXmlStr(from_dir, fName, fname, suffix)


def replaceXmlStr(from_dir, fName, fname, suffix):
    replaceStr = getData(f"{mCurrentPath}/scripts/repalce_layout/modify_ob/{fName}/ob_replaceStr{suffix}")
    targetStr = getData(f"{mCurrentPath}/scripts/repalce_layout/modify_ob/{fName}/ob_targetStr{suffix}")
    path = f"{from_dir}/res/layout/{fname}"
    with open(path, encoding='utf-8', mode='r') as rf:
        data = rf.read()
        data = data.replace(replaceStr, targetStr)
    with open(path, encoding='utf-8', mode='w') as wf:
        wf.write(data)


def getData(fpath):
    with open(fpath, encoding='utf-8', mode='r') as rf:
        return rf.read()


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


if __name__ == "__main__":
    mCurrentPath = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    parser.add_argument("to_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    to_dir = args.to_dir

    # from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.15.78/DecodeCode/Whatsapp_v2.24.15.78"
    # to_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.19.86/DecodeCode/Whatsapp_v2.24.19.86"

    replaceLayout(to_dir)
    delete_and_replace_files(f"{to_dir}/res/xml", f"{from_dir}/res/xml", ["GoldenApps.xml", "yo_widget_style.xml"])
    delete_and_replace_files(f"{to_dir}/res/layout", f"{from_dir}/res/layout", ["yo_settings.xml"])
    print("*******程序执行结束！*******")
