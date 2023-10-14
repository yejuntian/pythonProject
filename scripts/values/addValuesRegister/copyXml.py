import codecs
import json
import os
import lxml.etree as ET
import traceback

# 排除哪些文件夹
blacklist = ['.idea', '.git', '.gradle', 'build', 'lib', 'META-INF',
             'original', 'AndroidManifest.xml', 'apktool.yml']
# 只匹配下面的文件类型
extends = ["xml"]
# 文件名列表
fileNameList = ["arrays.xml", "attrs.xml", "bools.xml", "colors.xml",
                "dimens.xml", "ids.xml", "integers.xml", "strings.xml",
                "styles.xml"]
# 是否重命名style名称
isRenameStyle = False
# 需要copy的属性name字典
mappingData = {}

"""
    主要作用：根据noRegisterAttr.json配置属性，只进行copy属性，不进行public.xml属性注册操作
"""


def startCopyValues(from_dir, to_dir):
    global mappingData
    mappingData = getNameMappingList(f"{os.getcwd()}/noRegisterAttr.json")
    travelFolderCopyAttr(from_dir, to_dir)


def getNameMappingList(fpath):
    dict = {}
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = json.loads(rf.read())
        for attrType, nameList in data.items():
            if dict.get(attrType) is None:
                dict[attrType] = []
            for name in nameList:
                # 特殊处理
                if attrType == "style" and isRenameStyle:
                    name = name.replace("_", ".")
                # 去重操作
                if not name in dict[attrType]:
                    dict[attrType].append(name)
    return dict


def travelFolderCopyAttr(from_dir, to_dir):
    from_listdir = os.listdir(from_dir)
    to_listdir = os.listdir(to_dir)
    for fname in from_listdir:
        if not fname in blacklist:
            fpath = os.path.join(from_dir, fname)
            tpath = os.path.join(to_dir, fname)
            if os.path.isdir(fpath):
                # 不在目标目录，创建新文件夹
                if not fname in to_listdir:
                    os.makedirs(tpath, exist_ok=True)
                travelFolderCopyAttr(fpath, tpath)
            elif os.path.isfile(fpath):
                if fname.split(".")[-1] in extends and fname in fileNameList:
                    print(tpath)
                    startCopyAttr(fpath, tpath, fname.split(".")[0])


def startCopyAttr(fpath, tpath, fname):
    fileType = fname[0:len(fname) - 1]
    # 目标文件不存在
    if not os.path.exists(tpath):
        createNewFile(fpath, tpath, fileType)
    else:
        insertExitFile(fpath, tpath, fileType)


# 创建新文件插入diff code
def createNewFile(fpath, tpath, fileType):
    diffNameList = mappingData.get(fileType)
    if diffNameList is None or len(diffNameList) <= 0:
        return
    from_parser = ET.parse(fpath)
    from_root = from_parser.getroot()
    fromNameList = []
    isChanged: bool = False
    for fromChild in from_root:
        from_attr = fromChild.attrib
        from_attr_name = from_attr.get("name")
        if not from_attr_name is None and from_attr_name in diffNameList:
            isChanged = True
            fromNameList.append(fromChild)
    if isChanged:
        xml_content = convert_str(fromNameList)
        save_2_file(xml_content.replace('&gt;', '>'), tpath)


# diff code插入到已存在的文件
def insertExitFile(fpath, tpath, fileType):
    diffNameList = mappingData.get(fileType)
    if diffNameList is None or len(diffNameList) <= 0:
        return
    to_parser = ET.parse(tpath)
    to_root = to_parser.getroot()
    toNameList = []
    for toChild in to_root:
        to_attr = toChild.attrib
        to_attr_name = to_attr.get("name")
        if not to_attr_name is None:
            toNameList.append(to_attr_name)

    from_parser = ET.parse(fpath)
    from_root = from_parser.getroot()
    isChanged: bool = False
    for fromChild in from_root:
        from_attr = fromChild.attrib
        from_attr_name = from_attr.get("name")
        if not from_attr_name is None and not from_attr_name in toNameList and from_attr_name in diffNameList:
            isChanged = True
            to_root.append(fromChild)
    if isChanged:
        xml_content = convert_str(to_root)
        # 合并其他string.xml
        save_2_file(xml_content.replace('&gt;', '>'), tpath)


def convert_str(to_root):
    xml_content: str = '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
    sum = len(to_root)
    for index, child in enumerate(to_root):
        attr_tag = child.tag
        text = child.text
        xml_content += "    "
        # string/plurals标签中text内容">"会被转移为'&gt'
        if (attr_tag == "string" and str(text).__contains__(">")) or attr_tag == "plurals":
            child_str = ET.tostring(child, encoding="utf-8").decode('utf-8').strip().replace('&gt;', '>')
            xml_content += child_str
        else:
            xml_content += ET.tostring(child, encoding='utf-8').decode('utf-8').strip().replace('/>', ' />')
        if index < sum - 1:
            xml_content += '\n'

    xml_content += '\n</resources>\n'
    return xml_content


def save_2_file(data_str, target_file_path):
    try:
        with open(target_file_path, 'w+') as f:
            f.write(data_str)
    except Exception as result:
        print(f"写入{target_file_path}出现异常: {result}")
        print(traceback.format_exc())


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    to_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.23.20.76/DecodeCode/Whatsapp_v2.23.20.76"
    startCopyValues(f"{from_dir}/res", f"{to_dir}/res")
