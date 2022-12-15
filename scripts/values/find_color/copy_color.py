import codecs
import json
import os
import traceback
import lxml.etree as ET

# 所有color集合
nameList = []
# color.xml diff集合
diffNameList = []
# 需要插入的color集合
enableInsertNameList = []
# 排除哪些文件夹
blacklist = ['.idea', '.git', '.gradle', 'kotlin', 'lib', 'META-INF',
             'original', 'AndroidManifest.xml', 'apktool.yml']
# 只匹配下面的文件类型
extends = ["xml"]


def startCopyString(from_dir, to_dir):
    getNameList("color.json")
    getNameList("other_color.json")
    publicFilePath = os.path.join(to_dir, "res/values/public.xml")
    getInsertNameList(publicFilePath, "color")
    travelFolderCopyAttr(from_dir, to_dir, "colors.xml")
    insertPublic(publicFilePath, "color")
    print(f"程序执行结束，结果保存在{to_dir}")


def getNameList(fpath):
    with codecs.open(fpath, "r", "utf-8") as rf:
        data = json.loads(rf.read())
        for item in data:
            if not item in nameList:
                nameList.append(item)


def getInsertNameList(fpath, type):
    parser = ET.parse(fpath)
    root = parser.getroot()
    stringList = []
    for child in root:
        child_attr = child.attrib
        attr_name = child_attr.get("name")
        attr_type = child_attr.get("type")
        if not attr_name is None and not attr_type is None and type == attr_type:
            stringList.append(attr_name)

    # color标签diff集合
    for attrName in nameList:
        if not attrName in stringList:
            diffNameList.append(attrName)

    # print(diffNameList)


def travelFolderCopyAttr(from_dir, to_dir, typeName):
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
                travelFolderCopyAttr(fpath, tpath, typeName)
            elif os.path.isfile(fpath):
                if fname.split(".")[-1] in extends and fname == typeName:
                    print(tpath)
                    startCopyAttr(fpath, tpath)


def startCopyAttr(fpath, tpath):
    # 目标文件不存在
    if not os.path.exists(tpath):
        createNewFile(fpath, tpath)
    else:
        insertExitFile(fpath, tpath)


# 创建新文件插入diff code
def createNewFile(fpath, tpath):
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
            if not from_attr_name in enableInsertNameList:
                enableInsertNameList.append(from_attr_name)
    if isChanged:
        xml_content = convert_str(fromNameList)
        save_2_file(xml_content, tpath)


# diff code插入到已存在的文件
def insertExitFile(fpath, tpath):
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
            if not from_attr_name in enableInsertNameList:
                enableInsertNameList.append(from_attr_name)
    if isChanged:
        xml_content = convert_str(to_root)
        # 合并其他color.xml
        save_2_file(xml_content, tpath)


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


def insertPublic(fpath, type):
    to_parser = ET.parse(fpath)
    to_root = to_parser.getroot()
    maxChild = None
    maxId = 0
    for child in to_root:
        attr = child.attrib
        attrType = attr.get("type")
        attrId = attr.get("id")
        if not attrType is None and attrType == type:
            attrId = int(attrId, 16)
            if attrId >= maxId:
                maxId = attrId
                maxChild = child

    pos = to_root.index(maxChild)
    for itemName in enableInsertNameList:
        maxId += 1
        pos += 1

        element = ET.SubElement(to_root, "public")
        element.set("type", type)
        element.set("name", itemName)
        element.set("id", str(hex(maxId)))
        to_root.insert(pos, element)

    # 写入到public.xml文件中
    with codecs.open(fpath, "w+", encoding="utf-8") as wf:
        wf.write('<?xml version="1.0" encoding="utf-8"?>\n')
        wf.write('<resources>\n')
        for child in to_root:
            attrType = child.attrib.get("type")
            attrName = child.attrib.get("name")
            attrId = child.attrib.get("id")
            wf.write(f'    <public type="{attrType}" name="{attrName}" id="{attrId}" />\n')
        wf.write('</resources>')


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/wagb/DecodeCode/WhatsApp_v2.22.22.80"
    to_dir = "/Users/shareit/work/GBWorke/whatsapp_new/whatsapp_v2.22.25.11"
    startCopyString(from_dir, to_dir)
