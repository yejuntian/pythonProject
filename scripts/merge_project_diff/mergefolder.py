import os
import shutil

"""
    主要作用：在使用 apktool 反编译 APK 文件后，如果子目录中有多层子目录，
    将这些目录合并到一个新的目标目录中，方便查看新增了哪些smali文件。
"""


def merge_smali_files(project_path, target_dir):
    # 确保目标目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 获取以 'smali' 开头的子目录
    source_dirs = [os.path.join(project_path, d) for d in os.listdir(project_path)
                   if os.path.isdir(os.path.join(project_path, d)) and d.startswith('smali')]
    print("********** Smali files merged start **********")
    # 函数来合并 .smali 文件
    for src_dir in source_dirs:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith('.smali'):
                    # 计算相对路径
                    relative_path = os.path.relpath(root, src_dir)
                    target_path = os.path.join(target_dir, relative_path)

                    # 如果目标路径不存在，则创建它
                    if not os.path.exists(target_path):
                        os.makedirs(target_path)

                    # 复制 .smali 文件到目标路径
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_path, file)

                    if os.path.exists(target_file):
                        print(f"Warning: File {target_file} already exists and will be overwritten.")
                    shutil.copy2(source_file, target_file)

    print("********** Smali files merged end **********")
    traverse_and_replace(target_dir, "const-string/jumbo", "const-string")
    print(f"*********** 移除{project_path} 所有行号开始 ************")
    os.chdir(project_path)
    os.system("find . -name '*.smali' | xargs sed -i '' -E '/\.source[[:space:]]""/d; /\.line[[:space:]][0-9]+/d'")
    print(f"*********** 移除{project_path} 所有行号结束 ************")
    print(f"*********** 程序执行结束 ************")


def traverse_and_replace(from_dir, old_string, new_string):
    for root, dirs, files in os.walk(from_dir):
        for file in files:
            if file.endswith('.smali'):
                file_path = os.path.join(root, file)
                replace_string_in_file(file_path, old_string, new_string)


def replace_string_in_file(file_path, old_string, new_string):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_data = file.read()
    file_data = file_data.replace(old_string, new_string)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(file_data)


if __name__ == "__main__":
    # 替换为你的工程路径
    project_path = '/Users/shareit/work/androidProjects/EmptyProject/app-debug'
    target_dir = f'{project_path}/merged_smali'
    # 执行合并操作
    merge_smali_files(project_path, target_dir)
