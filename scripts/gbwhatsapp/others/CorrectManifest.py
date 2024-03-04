import codecs
import xml.etree.ElementTree as ET

# 用于保存activity属性name
activityNameList = set()
# android命名空间约束
android_scheme = "http://schemas.android.com/apk/res/android"
tagList = ["activity", "service"]

"""
    主要作用：匹配AndroidManifest.xml文件中,
    <intent-filter>中<action android:name="com.gbwhatsapp.intent.action.ENABLE_STICKER_PACK"/>
    矫正和Activity包名路径一致
    <intent-filter>中<action android:name="com.whatsapp.intent.action.ENABLE_STICKER_PACK"/>
"""


def matchManifest(from_dir):
    parserManifest(f"{from_dir}/AndroidManifest.xml")


def parserManifest(fpath):
    ET.register_namespace('android', android_scheme)
    nameSpace = "{" + android_scheme + "}"
    attrName = f"{nameSpace}name"
    parse = ET.parse(fpath)
    root = parse.getroot()
    for child in root:
        childTag = child.tag
        if childTag == "application":
            for subChild in child:
                subChildTag = subChild.tag
                subChildAttr = subChild.attrib
                subAttName = subChildAttr.get(attrName)
                subChildStr = ET.tostring(subChild, encoding="utf-8").decode('utf-8')
                if subChildStr.__contains__("<action") and subAttName.__contains__("com.whatsapp"):
                    print(subAttName)
                    for filter in subChild:
                        for filterSub in filter:
                            filter_sub_attrib = filterSub.attrib
                            filter_sub_tag = filterSub.tag
                            filter_sub_attr = filterSub.attrib
                            if filter_sub_tag == "action":
                                filter_sub_attrib[attrName] = filter_sub_attr.get(attrName).replace("com.gbwhatsapp", "com.whatsapp")

    data_str = ET.tostring(root, encoding="utf-8").decode('utf-8').replace(' />', '/>')
    write_2_file(fpath, data_str)


def write_2_file(file_path, data_str):
    xml_data = f'<?xml version="1.0" encoding="utf-8" standalone="no"?>{data_str}'
    try:
        with codecs.open(file_path, mode='w+', encoding="utf-8") as f:
            f.write(xml_data)
    except Exception as result:
        print(f"写入{file_path}异常: {result}")


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/shareit/gbwhatsapp_2.24.3.81/DecodeCode/Whatsapp_v2.24.3.81"
    matchManifest(from_dir)
