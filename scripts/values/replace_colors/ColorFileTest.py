import codecs
import json
import xml.etree.ElementTree as ET
import traceback

# 存储对应关系文件
# oldColorPath = 'scripts/values/replace_colors/colors_old.json'
oldColorPath = 'colors_old.json'
# 颜色属性名称集合-->values/colors.xml
colorNameList = set()
# color内容引用集合-->values/colors.xml
colorTxtList = set()
# 颜色属性名称集合-->values-night/colors.xml
colorNameList2 = set()
# color内容引用集合-->values-night/colors.xml
colorTxtList2 = set()


# 校验color正确性，并把矫正color写入到color.xml
def correctColorFile():
    oldColorList = loadOldColorData(oldColorPath)
    loadNewColorData(fColorPath, False, oldColorList)
    loadNewColorData(fColorNightPath, True, oldColorList)
    correctColorData(False)
    correctColorData(True)


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
                print(f'{from_path} <color name="{colorName}">矫正为:{correctColor}</color>')
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
def correctColorData(isNightColor):
    if not isNightColor:
        for colorTxt in colorTxtList:
            if not colorTxt in colorNameList and not colorTxt in colorNameList2:
                print(f'{fColorPath}  <color name="{colorTxt}">未找到</color>>')
    else:
        for colorTxt in colorTxtList2:
            if not colorTxt in colorNameList2 and not colorTxt in colorNameList:
                print(f'{fColorNightPath}  <color name="{colorTxt}">未找到</color>>')


if __name__ == '__main__':
    from_path = "/Users/shareit/work/shareit/gbwhatsapp_2.23.8.76/DecodeCode/Whatsapp_v2.23.8.76"
    fColorPath = f"{from_path}/res/values/colors.xml"
    fColorNightPath = f"{from_path}/res/values-night/colors.xml"
    correctColorFile()
