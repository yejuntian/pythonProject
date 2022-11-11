import argparse
import os
import shutil
import time
import manifest_diff
import merge_xml_diff

# 排除哪些文件夹
black_list_dir = ['.idea', ".git", 'build', 'apktool.yml']
# 目标项目的地址
target_project_path = ""
# 用于存放diff数据集合，key是
dir_map = {}
# 是否被允许copy到其他文件夹
is_allow: bool = False

"""
    对比两个项目的diff之处，把新增文件和xml属性copy到目标项目中
    project_from_dir：代码多的目录
    project_to_dir：代码少的目录
"""


def execute_merge_diff_file(project_from_dir, project_to_dir):
    """
    project_from_dir:要复制的项目地址(代码多)
    project_to_dir：目标项目的地址(代码少)
    """
    list_from_dir = os.listdir(project_from_dir)
    list_to_dir = os.listdir(project_to_dir)

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
                # 继续递归遍历文件夹
                execute_merge_diff_file(from_file_path, to_file_path)
            elif os.path.isfile(from_file_path):
                if from_path not in list_to_dir:
                    if is_allow:
                        shutil.copy(from_file_path, to_file_path)
                        # print(to_file_path)
                    else:
                        # 项目diff目录
                        diff_dir = str(to_file_path)
                        diff_project_path = f'{target_project_path}_diff{diff_dir.replace(target_project_path, "")}'
                        diff_folder_path = os.path.dirname(diff_project_path)
                        # print(diff_folder_path)
                        if not os.path.exists(diff_folder_path):
                            os.makedirs(diff_folder_path, exist_ok=True)
                        shutil.copy(from_file_path, diff_project_path)

                # res下values目录特殊处理
                if from_file_path.__contains__("/res/values"):
                    if is_allow:
                        merge_xml_diff.merge_diff(from_file_path, to_file_path)
                    else:
                        merge_xml_diff.merge_diff_attrs(from_file_path, to_file_path, target_project_path)
                if from_file_path.__contains__("AndroidManifest") and not from_file_path.__contains__("original"):
                    if not is_allow:
                        manifest_diff.merge_manifest_diff(to_file_path, from_file_path)
                        fromDir = project_from_dir + "/AndroidManifest_diff.xml"
                        if os.path.exists(fromDir):
                            shutil.move(fromDir, project_to_dir + "_diff")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_from_dir")
    parser.add_argument("project_to_dir")
    args = parser.parse_args()

    from_dir = args.project_from_dir
    to_dir = args.project_to_dir
    target_project_path = to_dir
    operate_flag = input(f'是否将diff文件输出到:{to_dir}\nyes or no ？\n')
    is_allow = operate_flag == "yes"
    before = time.time()
    execute_merge_diff_file(from_dir, to_dir)
    after = time.time()
    print(f"输出diff完成，写入到{to_dir if is_allow == True else to_dir + '_diff'} , 耗时{after - before} 秒")
