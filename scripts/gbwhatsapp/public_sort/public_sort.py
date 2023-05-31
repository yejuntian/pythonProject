import argparse
import codecs
import functools
import traceback
import xml.etree.ElementTree as ET

public_data_list = []

"""
    主要作用：对public.xml资源进行升序排序，
    并把排序结果输出到public_sorted.xml中
"""


class PublicEntity:
    # 定义基本属性
    public_type = ""
    public_name = ""
    public_id = 0

    # 定义构造方法
    def __init__(self, public_type, public_name, public_id):
        self.public_type = public_type
        self.public_name = public_name
        self.public_id = int(public_id, 16)

    def __repr__(self) -> str:
        return f'<public type="{self.public_type}" name="{self.public_name}"id="{hex(self.public_id)}" />'


def sort_func(bean1, bean2):
    a = bean1.public_id
    b = bean2.public_id
    if a > b:
        return 1
    elif a < b:
        return -1
    else:
        result = f'资源ID出现重复,请重新命名：<public type="{bean2.public_type}" name="{bean2.public_name}" id="{bean2.public_id}" />'
        raise Exception(result)


def public_sort(from_path):
    fpath = f"{from_path}/res/values/public.xml"
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        public_type: str = child.attrib["type"]
        public_name: str = child.attrib["name"]
        # 十六进制转十进制
        public_id: str = child.attrib["id"]
        if public_id.startswith("0x"):
            attr_id: int
            try:
                attr_id = int(public_id, 16)
            except Exception:
                print(f"错误异常：{traceback.format_exc()}")
                result = f'错误原因：资源ID命名错误,：<public type="{public_type}" name="{public_name}" id="{public_id}" />'
                raise Exception(result)

            if attr_id <= int("0xffffffff", 16):
                entity = PublicEntity(public_type, public_name, public_id)
                public_data_list.append(entity)
            else:
                result = f'错误原因：资源ID超过最大值0xffffffff,请重新命名资源ID数值：<public type="{public_type}" name="{public_name}" id="{public_id}" />'
                raise Exception(result)
        else:
            result = f'错误原因：资源ID请以0x命名,：<public type="{public_type}" name="{public_name}" id="{public_id}" />'
            raise Exception(result)
    public_data_list.sort(key=functools.cmp_to_key(sort_func))


def save_to_file(data_list, file_name):
    print(file_name)
    with codecs.open(file_name, "w+", encoding="utf-8") as wf:
        wf.write('<?xml version="1.0" encoding="utf-8"?>\n')
        wf.write('<resources>\n')
        for bean in data_list:
            wf.write(f'    <public type="{bean.public_type}" name="{bean.public_name}" id="{hex(bean.public_id)}" />\n')
        wf.write('</resources>')


def sort(from_path, isRenameFile=False):
    public_sort(from_path)
    target_file = from_path + "/res/values/public_sorted.xml"
    if isRenameFile:
        target_file = from_path + "/res/values/public.xml"
    save_to_file(public_data_list, target_file)
    print(f"public.xml排序完成,排序结果保存到:{target_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_path")
    args = parser.parse_args()
    sort(args.from_path)
