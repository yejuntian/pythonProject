import argparse
import codecs
import os

# 替换的键值对，一行两个字符串，前面的是旧字符串，后面的是新字符串，中间用空格隔开
config_path = 'scripts/replacepackage/config.properties'
# 只匹配下面的文件类型
extends = ["smali", "xml", "html"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'META-INF', 'original', 'apktool.yml']
# 默认包名集合列表
default_package_list = ["com.obwhatsapp", "com.WhatsApp2Plus"]
# 用来保存properties配置的集合
mapping_string = {}

"""
    主要作用：替换OB、Plus各自包名对应的关键字符串如下：
    OB:GBWhatsApp->OBWhatsApp。
    plus:GBWhatsApp->WhatsApp。
"""


# 加载replacekeys.properties配置文件
def load_replace_keys(file_path, map_string):
    # 读取 properties 文件
    with codecs.open(file_path, "r", "utf-8") as rfile:
        for line in rfile.readlines():
            # 去掉行首行尾空格和换行符
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith('#'):
                continue
            if line.__contains__(r"\uD83C\uDFB5"):
                line = line.replace(r"\uD83C\uDFB5", "🎵")
                if line.find('🎵') > 0:
                    strs = line.split('🎵')
                    map_string[strs[0].strip()] = strs[1].strip()


def execute_path(folder_path, black_list, extends, mapping_string):
    os.chdir(folder_path)
    cwd = os.getcwd()
    dirs = os.listdir(cwd)
    for tmp in dirs:
        # 排除blacklist文件夹
        if tmp not in black_list:
            fpath = os.path.join(cwd, tmp)
            if os.path.isfile(fpath):
                print('fpath=', fpath)
                # 只extends的文件类型
                if fpath.split('.')[-1] in extends:
                    with codecs.open(fpath, "r", "utf-8") as rfile:
                        data = rfile.read()
                    with codecs.open(fpath, "w", "utf-8") as wfile:
                        replace_times = 0
                        for key, value in mapping_string.items():
                            replace_times += data.count(key)
                            data = data.replace(key, value)
                        print(r'替换次数：', replace_times)
                        wfile.write(data)
            # 如果是文件夹，递归
            elif os.path.isdir(fpath):
                execute_path(fpath, blacklist, extends, mapping_string)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_path")
    args = parser.parse_args()
    folder_path = args.folder_path

    load_replace_keys(config_path, mapping_string)
    execute_path(folder_path, blacklist, extends, mapping_string)
    print(f"执行完毕，输出结果保存到{folder_path}")
