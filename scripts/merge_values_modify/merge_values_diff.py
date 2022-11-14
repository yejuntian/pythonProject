import argparse
import os
import xml.etree.ElementTree as ET

data_map = {}

"""
    主要作用：values目录下根据diff_attrs.xml属性配置，
    合并新增或者修改的属性写入到目标文件中
"""


class ValuesAttrs:
    def __init__(self, parentTagName, subTag, subTagName, subTagTxt, ):
        self.parentTagName = parentTagName  # 父标签属性name
        self.subTag = subTag  # 子标签tag
        self.subTagName = subTagName  # 子标签属性name
        self.subTagTxt = subTagTxt  # 子标签文本内容

    def __repr__(self) -> str:
        return f'parentTagName="{self.parentTagName}" subTag="{self.subTag}" subTagName="{self.subTagName}" subTagTxt="{self.subTagTxt}"/>'


def load_data(xml_path):
    parse = ET.parse(xml_path)
    root = parse.getroot()
    scheme = "http://www.w3.org/XML/1998/namespace"
    nameSpace = "{" + scheme + "}"
    for child in root:
        fileName = child.attrib.get("name")
        subTag = child.attrib.get("select")
        data_list = []
        for sub in child:
            subAttr = sub.attrib
            parentTagName = subAttr.get(f"{nameSpace}id")
            subTagName = subAttr.get(f"{nameSpace}lang")
            subTagTxt = sub.text.strip()
            data_list.append(ValuesAttrs(parentTagName, subTag, subTagName, subTagTxt))
        data_map[fileName] = data_list


def merge_values_modify(from_dir):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath) and fpath.__contains__("res"):
            merge_values_modify(fpath)
        elif os.path.isfile(fpath):
            if fpath.__contains__("values/") and fname in data_map.keys():
                save_2_file(fpath, data_map.get(fname))


def save_2_file(fpath, dataList):
    global sub_attr_name
    fname = os.path.basename(fpath)
    nameList = []
    for attrBean in dataList:
        nameList.append(attrBean.parentTagName)

    parser = ET.parse(fpath)
    root = parser.getroot()
    for child in root:
        attr = child.attrib
        attr_name = attr.get("name")
        if attr_name in nameList:
            bean = dataList[nameList.index(attr_name)]
            text = bean.subTagTxt
            if fname == "strings.xml":
                child.text = text
            else:
                isExitLabel = False
                for subChild in child:
                    subChildName = subChild.attrib.get("name")
                    sub_attr_name = bean.subTagName
                    if (not subChildName is None) and subChildName == sub_attr_name:  # 存在指定子节点
                        isExitLabel = True
                        subChild.text = bean.subTagTxt
                        break

                if not isExitLabel:  # 不存在指定子节点，则进行插入
                    element = ET.Element(bean.subTag)
                    if not sub_attr_name is None:
                        element.attrib = {"name": sub_attr_name}
                    element.text = f"{text}"
                    child.append(element)

    write_2_file(fpath, convert_str(root))


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
            xml_content += ET.tostring(child, encoding='utf-8').decode('utf-8').strip()
        if index < sum - 1:
            xml_content += '\n'

    xml_content += '\n</resources>\n'
    return xml_content


def write_2_file(file_path, data_str):
    try:
        with open(file_path, 'w+') as f:
            f.write(data_str)
    except Exception as result:
        print(f"写入{file_path}出现异常: {result}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    load_data("scripts/merge_values_modify/diff_attrs.xml")
    merge_values_modify(args.from_dir)
    print("**************程序执行结束**************")
