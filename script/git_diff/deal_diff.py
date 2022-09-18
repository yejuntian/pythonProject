import argparse
import codecs
import json
import os
import shutil

add_file_list = []
modify_file_list = []
del_file_list = []
other_file_list = []


def exec_diff(diff_path):
    with codecs.open(diff_path, mode="r", encoding="utf-8") as refile:
        lines = refile.readlines()
        for line in lines:
            split_line = line.strip().split("	")
            operate = split_line[0]
            file = split_line[1]
            if operate == "M":
                modify_file_list.append(file)
            elif operate == "D":
                del_file_list.append(file)
            elif operate == "A":
                add_file_list.append(file)
            else:
                other_file_list.append(file)


def save_data_to_file(data_list, file_name):
    json_dump = json.dumps(data_list, ensure_ascii=False, indent=2)
    with codecs.open(file_name, "w+", encoding="utf-8") as wf:
        wf.write(json_dump)


def move_file_to_new_folder(data_list, cur_path, dir_name):
    fold_path = f"{cur_path}/{dir_name}"
    print(f"fold_path = {fold_path}")
    # 创建目标目录
    if not os.path.exists(fold_path):
        os.makedirs(fold_path, exist_ok=True)
    os.chdir(cur_path)
    print(f"current_path = {os.getcwd()}")
    for data in data_list:
        first_index = data.find("/")
        last_index = data.rfind("/")
        file_name = os.path.basename(data)

        new_fold_path = fold_path + data[first_index:last_index + 1]
        new_file_path = new_fold_path + file_name
        if not os.path.exists(new_fold_path):
            os.makedirs(new_fold_path, exist_ok=True)
        shutil.copy(data, new_file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("diff_path")
    args = parser.parse_args()
    exec_diff(args.diff_path)
    # 根据git提交类型，分别存到到不同文件中
    mCurrentPath = os.getcwd()
    os.chdir(mCurrentPath + "/script/git_diff")
    save_data_to_file(add_file_list, "add.json")
    save_data_to_file(modify_file_list, "modify.json")
    save_data_to_file(del_file_list, "del.json")
    save_data_to_file(other_file_list, "other.json")
    # 移动新增文件到指定目录
    move_file_to_new_folder(add_file_list, mCurrentPath, "outputFiles")
    print(f"执行脚本完毕，输入结果到:${mCurrentPath}/outputFiles")
