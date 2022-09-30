import argparse
import os
import shutil

# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'kotlin', 'lib', 'META-INF',
             'original', 'AndroidManifest.xml', 'apktool.yml']
# 要复制的icon列表
icon_list = ["share_self.jpg", "about_logo.png", "icon.png",
             "splash_logo.png", "ic_wa_foreground.png", "img_0.png",
             "img_1.png", "background.jpg"]

"""
    主要作用：根据"icon_list"图片资源列表，
    遍历复制的目录列表找到对应图片，并替换目标目录对应图片
"""


def replace_icon(from_path, to_path, black_list):
    from_listdir = os.listdir(from_path)
    for file_name in from_listdir:
        from_file_path = os.path.join(from_path, file_name)
        to_file_path = os.path.join(to_path, file_name)
        if file_name not in black_list and not file_name.__contains__("smali"):
            if os.path.isdir(from_file_path):
                # 过滤不需要遍历的文件夹
                if enable_traver(file_name, "layout") and enable_traver(file_name, "values") and enable_traver(
                        file_name, "xml"):
                    # print(f"遍历文件：{file_name}")
                    replace_icon(from_file_path, to_file_path, blacklist)
                else:
                    continue
            else:
                if file_name in icon_list:
                    if not os.path.exists(to_path):
                        os.makedirs(to_path, exist_ok=True)
                    shutil.copyfile(from_file_path, to_file_path)


def enable_traver(file_name, folder_name):
    return not file_name.__contains__(folder_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_project_dir")
    parser.add_argument("to_project_dir")
    args = parser.parse_args()

    replace_icon(args.from_project_dir, args.to_project_dir, blacklist)
    print(f"执行完成，输出结果保存到：{args.to_project_dir}")
