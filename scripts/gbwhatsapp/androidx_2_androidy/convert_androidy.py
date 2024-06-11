import argparse
import codecs
import glob
import os
import shutil
import time

# 只匹配下面的文件类型
extends = ["smali", "xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'lib',
             'META-INF', 'original', 'apktool.yml']
"""
    主要作用：androidx变为androidy
"""


# 由anroidx目录 变为 androidy
def change_androidx_2_androidy(from_dir):
    file_list = glob.glob(f"{from_dir}/smali*/androidx/**/*.smali", recursive=True)
    for file_path in file_list:
        to_file_path = file_path.replace("androidx", "androidy")
        file_dir = os.path.dirname(to_file_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir, exist_ok=True)
        shutil.move(file_path, to_file_path)


# 遍历文件，字符串"androidx"替换为"androidy"
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


def convertAndroidY(from_dir):
    before_time = time.time()
    change_androidx_2_androidy(from_dir)
    traverse_folder(from_dir, {"androidx": "androidy"})
    after_time = time.time()
    print(f"执行完毕，输出结果保存到：{from_dir} 共耗时{after_time - before_time} 秒")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    convertAndroidY(args.from_dir)
