import os
import re
import json
import codecs

# 定义正则表达式和替换映射
regex_str = r"0x7f[0-9a-f]{6}"
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'lib', 'META-INF',
             'original', 'res', 'smali', 'smali_classes2', 'smali_classes3',
             'smali_classes4', 'smali_classes5', 'AndroidManifest.xml', 'apktool.yml']
# 只匹配下面的文件类型
extends = ["smali"]


def replace_strings_in_smali_file(file_path, replacement_map):
    with open(file_path, 'r', encoding='utf-8') as file:
        smali_content = file.read()

    # 使用正则表达式查找字符串
    matches = re.findall(regex_str, smali_content)

    # 根据映射替换字符串
    for match in matches:
        if match in replacement_map:
            if match == "0x7f040dc8":
                print("")
            # replacement_value = re.sub("0x7f[0-9a-f]{6}", lambda x: x.group()[:] + '🎵;', replacement_map[match])
            replacement_value = replacement_map[match]
            replaced_value = replacement_value[:4] + "🎵" + replacement_value[4:]
            smali_content = smali_content.replace(match, replaced_value)

    # 将替换后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(smali_content)


def replaceId(folder_path, mappingData):
    if os.path.isdir(folder_path):
        dirs = os.listdir(folder_path)
        for fileName in dirs:
            file_path = os.path.join(folder_path, fileName)
            if os.path.isfile(file_path) and file_path.split('.')[-1] in extends:
                replace_strings_in_smali_file(file_path, mappingData)
            elif os.path.isdir(file_path) and fileName not in blacklist:
                replaceId(file_path, mappingData)
    else:
        replace_strings_in_smali_file(folder_path, mappingData)


# 替换🎵符为空字符串""
def replaceStr(folder_path):
    os.chdir(folder_path)
    cwd = os.getcwd()
    if os.path.isdir(cwd):
        dirs = os.listdir(cwd)
        for fileName in dirs:
            file_path = os.path.join(cwd, fileName)
            if os.path.isfile(file_path) and file_path.split('.')[-1] == "smali":
                with codecs.open(file_path, "r", "utf-8") as rfile:
                    data = rfile.read()
                with codecs.open(file_path, "w", "utf-8") as wfile:
                    data = data.replace("🎵", "")
                    wfile.write(data)
            elif os.path.isdir(file_path):
                replaceStr(file_path)
    else:
        replaceStr(cwd)


def replace_strings_in_directory(directory, mappingPath):
    with open(mappingPath, "r") as f:
        replacement_map = json.loads(f.read())
    replaceId(directory, replacement_map)
    replaceStr(directory)


if __name__ == "__main__":
    directory_path = "/Users/shareit/work/shareit/gbwhatsapp_2.23.25.76/DecodeCode/Whatsapp_v2.23.25.76/smali_classes7/com/applovin/sdk"
    mappingPath = "/Users/shareit/work/pythonProject/scripts/matchPublicId.json"
    # 执行替换操作
    replace_strings_in_directory(directory_path, mappingPath)
    print("--------程序执行结束------------")
