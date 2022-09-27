import argparse
import os
import shutil

import merge_xml_diff

# 排除哪些文件夹
black_list_dir = ['.idea', ".git", 'build', 'AndroidManifest.xml', 'apktool.yml']
# 用于存放diff数据集合，key是
dir_map = {}

"""
    对比两个项目的diff之处，把新增文件和xml属性copy到目标项目中
"""


def execute_merge_diff_file(project_from_dir, project_to_dir):
    """
    project_from_dir:要复制的项目地址
    project_to_dir：目标项目的地址
    """
    list_from_dir = os.listdir(project_from_dir)
    list_to_dir = os.listdir(project_to_dir)
    data_list = []

    # print(f"from_dir = {project_from_dir} to_dir = {project_to_dir}")
    # print(list_from_dir)
    for from_path in list_from_dir:
        # 要复制的目录
        from_file_path = project_from_dir + os.sep + from_path
        # 目标目录
        to_file_path = project_to_dir + os.sep + from_path
        # 不在黑名单中的文件
        if from_path not in black_list_dir:
            if os.path.isdir(from_file_path):
                # 不在目标目录，创建新文件夹
                if from_path not in list_to_dir:
                    os.makedirs(to_file_path, exist_ok=True)
                    data_list.append(os.path.dirname(from_file_path))
                execute_merge_diff_file(from_file_path, to_file_path)
                # print(data_list)
            elif os.path.isfile(from_file_path):
                if from_path not in list_to_dir:
                    shutil.copy(from_file_path, to_file_path)
                # res下values目录特殊处理
                if from_file_path.__contains__("/res/values"):
                    merge_xml_diff.merge_diff_attrs(from_file_path, to_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_from_dir")
    parser.add_argument("project_to_dir")
    args = parser.parse_args()

    execute_merge_diff_file(args.project_from_dir, args.project_to_dir)
