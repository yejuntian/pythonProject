import os
import shutil
import codecs
import glob
import argparse
import time

# 只匹配下面的文件类型
extends = ["smali", "xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin',
             'lib', 'META-INF', 'original', 'apktool.yml']
# 用于保存类对应关系集合
data_map = {}
"""
    主要作用：support变为supporty
"""


# 由support目录 变为 supporty,并设置类名的对应关系
def change_support_2_supporty(from_dir):
    file_list = glob.glob(f"{from_dir}/smali/android/support/**/*.smali", recursive=True)
    for file_path in file_list:
        from_file_path = file_path
        to_file_path = file_path.replace("android/support", "android/supporty")
        file_dir = os.path.dirname(to_file_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir, exist_ok=True)
        shutil.move(file_path, to_file_path)
        # 设置类名的对应关系
        set_data_map(from_dir, from_file_path, to_file_path)

# 设置类名的对应关系
def set_data_map(file_dir, from_file_path, to_file_path):
    old_class_path1 = from_file_path[len(f"{file_dir}/smali") + 1:].split(".")[0]
    old_class_path2 = old_class_path1.replace("/", ".")

    new_class_path1 = to_file_path[len(f"{file_dir}/smali") + 1:].split(".")[0]
    new_class_path2 = new_class_path1.replace("/", ".")

    data_map[old_class_path1] = new_class_path1
    data_map[old_class_path2] = new_class_path2


# 遍历文件，替换为data_map中的字符串
def traverse_folder(from_dir, data_map):
    listdir = os.listdir(from_dir)
    for filename in listdir:
        file_path = str(os.path.join(from_dir, filename))
        print(file_path)
        if filename not in blacklist:
            if os.path.isdir(file_path):
                traverse_folder(file_path, data_map)
            elif os.path.isfile(file_path):
                if file_path.split(".")[-1] in extends:
                    save_2_file(file_path, data_map)


# 保存到文件中
def save_2_file(fpath, package_map_data):
    with codecs.open(fpath, "r", "utf-8") as rfile:
        data = rfile.read()
    with codecs.open(fpath, "w", "utf-8") as wfile:
        replace_times = 0
        for key, value in package_map_data.items():
            replace_times += data.count(key)
            data = data.replace(key, value)
        print(r'替换次数：', replace_times)
        wfile.write(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir

    before_time = time.time()
    change_support_2_supporty(from_dir)
    traverse_folder(from_dir, data_map)
    after_time = time.time()
    print(f"执行完毕，输出结果保存到：{from_dir} 共耗时{after_time - before_time} 秒")
