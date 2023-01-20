import argparse
import codecs
import json
import os
import traceback
import xml.etree.ElementTree as ET

# 只匹配下面的文件类型
extends = ["xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin',
             'lib', 'META-INF', 'original', 'apktool.yml']
# 存储对应关系文件
colorPath = 'scripts/values/replace_colors/colorMapping.json'

# ************下面用于判断color是否正确******************
# 存储对应关系文件
# oldColorPath = 'scripts/values/replace_colors/colors_old.json'
oldColorPath = 'scripts/values/replace_colors/colors_old.json'
# 颜色属性名称集合-->values/colors.xml
colorNameList = set()
# color内容引用集合-->values/colors.xml
colorTxtList = set()
# 颜色属性名称集合-->values-night/colors.xml
colorNameList2 = set()
# color内容引用集合-->values-night/colors.xml
colorTxtList2 = set()

"""
    主要作用：根据colors.json中对应关系，
    替换项目所涉及的colors.xml对应的属性name
"""


def replaceColors():
    mapping_string = load_replace_keys(colorPath)
    execute_folder(from_dir, blacklist, extends, mapping_string)


def load_replace_keys(dataPath):
    with codecs.open(dataPath, "r", "utf-8") as rfile:
        return json.loads(rfile.read())


def execute_folder(from_dir, blacklist, extends, mapping_string):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        if fname not in blacklist:
            fpath = os.path.join(from_dir, fname)
            if os.path.isdir(fpath):
                execute_folder(fpath, blacklist, extends, mapping_string)
            elif os.path.isfile(fpath):
                if fname.split(".")[-1] in extends:
                    print(fpath)
                    enableRenameFile = False
                    with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
                        data = rf.read()
                    with codecs.open(fpath, mode="w", encoding="utf-8") as wf:
                        replace_times = 0
                        for key, value in mapping_string.items():
                            if key.startswith("APKTOOL_DUMMYVAL_"):
                                replace_times += data.count(key)
                                data = data.replace(key, value)
                                if key == fname.split(".")[0]:
                                    enableRenameFile = True
                                    newPath = os.path.join(from_dir, f"{value}.xml")
                        print(r'替换次数：', replace_times)
                        wf.write(data)
                        # 重命名文件
                        if enableRenameFile:
                            os.rename(fpath, newPath)


# 校验color正确性，并把矫正color写入到color.xml
def correctColorFile(from_dir):
    fColorPath = f"{from_dir}/res/values/colors.xml"
    fColorNightPath = f"{from_dir}/res/values-night/colors.xml"
    oldColorList = loadOldColorData(oldColorPath)
    loadNewColorData(fColorPath, False, oldColorList)
    loadNewColorData(fColorNightPath, True, oldColorList)
    correctColorData(False, fColorPath, fColorNightPath)
    correctColorData(True, fColorPath, fColorNightPath)


def loadOldColorData(fpath):
    colorMap = {}
    with codecs.open(fpath, "r", "utf-8") as rfile:
        jsonData = json.loads(rfile.read())
        for item in jsonData:
            colorMap[item["colorName"]] = item["curColor"]
    return colorMap


def loadNewColorData(from_path, isNightColor, colorMap):
    enableCorrect = False
    parse = ET.parse(from_path)
    root = parse.getroot()
    for child in root:
        attrib = child.attrib
        colorName = attrib.get("name")
        curColor = child.text
        if not isNightColor:
            colorNameList.add(colorName)
        else:
            colorNameList2.add(colorName)
        if curColor.startswith("@color/"):
            colorName2 = curColor.split("/")[1]
            if colorName == colorName2:
                correctColor = getCorrectColor(colorMap.get(colorName2))
                child.text = correctColor
                enableCorrect = True
                print(f'{from_path}  <color name="{colorName}">颜色已矫正为：{correctColor}</color>>')
            if not isNightColor:
                colorTxtList.add(colorName2)
            else:
                colorTxtList2.add(colorName2)

    if enableCorrect:
        colorContent = convert_str(root)
        try:
            with open(from_path, 'w+') as f:
                f.write(colorContent)
        except Exception as result:
            print(f"写入{from_path}出现异常: {result}")
            print(traceback.format_exc())


# 写入文件
def convert_str(to_root):
    xml_content: str = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    sum = len(to_root)
    for index, child in enumerate(to_root):
        xml_content += "    "
        xml_content += ET.tostring(child, encoding='utf-8').decode('utf-8').strip().replace('/>', ' />')
        if index < sum - 1:
            xml_content += '\n'
    xml_content += '\n</resources>\n'
    return xml_content


def getCorrectColor(colorTxt):
    if not colorTxt is None and colorTxt.__contains__("$"):
        return colorTxt.split("$")[1]
    return colorTxt


# 校验color是否正确
def correctColorData(isNightColor, fColorPath, fColorNightPath):
    if not isNightColor:
        for colorTxt in colorTxtList:
            if not colorTxt in colorNameList and not colorTxt in colorNameList2:
                print(f'{fColorPath}  <color name="{colorTxt}">未找到</color>>')
    else:
        for colorTxt in colorTxtList2:
            if not colorTxt in colorNameList2 and not colorTxt in colorNameList:
                print(f'{fColorNightPath}  <color name="{colorTxt}">未找到</color>>')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()

    from_dir = args.from_dir
    replaceColors()
    correctColorFile(from_dir)
