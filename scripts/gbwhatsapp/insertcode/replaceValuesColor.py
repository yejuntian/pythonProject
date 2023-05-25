import os.path
import codecs
import lxml.etree as ET
import argparse

"""
 主要作用：读取并解析from_dir/res/res/values-v31/colors.xml，目录下的xml文件，
 把@android:color/system_XXX这种格式的xml内容，替换为@*android:color/system_XXX这种格式。
"""


def replaceColors(from_dir):
    targetFilePath = f"{from_dir}/res/values-v31/colors.xml"
    if os.path.exists(targetFilePath):
        startReplaceColors(targetFilePath)


def startReplaceColors(fpath):
    parser = ET.parse(fpath)
    root = parser.getroot()
    for child in root:
        text = child.text
        if text.startswith("@android:"):
            text = text.replace("@android:", "@*android:")
            child.text = text
    data_str = ET.tostring(root, encoding="utf-8").decode('utf-8').replace(' />', '/>')
    write_2_file(fpath, data_str)


def write_2_file(file_path, data_str):
    xml_data = f'<?xml version="1.0" encoding="utf-8"?>\n{data_str}'
    try:
        with codecs.open(file_path, mode='w+', encoding="utf-8") as f:
            f.write(xml_data)
    except Exception as result:
        print(f"写入{file_path}异常: {result}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # from_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/whatsapp_1"
    replaceColors(from_dir)
