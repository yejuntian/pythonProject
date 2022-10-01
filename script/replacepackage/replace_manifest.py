import argparse
import codecs

import lxml.etree as ET

# 默认包名集合列表
default_package_list = ["com.gbwhatsapp", "com.obwhatsapp", "com.WhatsApp2Plus", "com.yowhatsapp"]
# 新包名集合列表
new_package_list = default_package_list.copy()
# android命名空间约束
android_scheme = "http://schemas.android.com/apk/res/android"


def replace_manifest(public_dir, default_package, new_package):
    """
        public_dir:AndroidManifest.xml路径
        default_index：默认包名对应的index
        new_index：新包对应的index
    """
    replace_package(public_dir, default_package, new_package)
    parse_manifest(public_dir, new_package)


# 换包
def replace_package(file_path, default_package, new_package):
    try:
        with codecs.open(file_path, "r", "utf-8") as rf:
            data = rf.read()
            data = data.replace(default_package, new_package)
        with codecs.open(file_path, 'w+', "utf-8") as wf:
            wf.write(data)
    except Exception as result:
        print("replace_package 出现异常".center(8, "-"))
        print(result)


# 解析androidManifest.xml
def parse_manifest(file_path, new_package):
    ET.register_namespace('android', android_scheme)
    tree = ET.parse(file_path)
    root = tree.getroot()
    # print('root-tag:', root.tag, ',root-attrib:', root.attrib, ',root-text:', root.text)
    for child in root:
        # print('child-tag是：', child.tag, ',child.attrib：', child.attrib, ',child.text：', child.text)
        for sub in child:
            # print('sub-tag是：', sub.tag, ',sub.attrib：', sub.attrib, ',sub.text：', sub.text)
            replace_san_sdk(sub, new_package)
    data_str = ET.tostring(root, encoding="utf-8").decode('utf-8').replace(' />', '/>')
    write_2_file(file_path, data_str)


# 替换sanSdk配置信息
def replace_san_sdk(subLable, new_package):
    tagLable = subLable.tag
    if "meta-data" == tagLable:
        nameSpace = "{" + android_scheme + "}"
        sanName = str(subLable.attrib[nameSpace + "name"])
        sanKey, sanValue = getSanSdkInfo(new_package)
        if sanName == "com.san.APP_KEY":
            subLable.attrib[nameSpace + "value"] = sanKey
        elif sanName == "com.san.san-sdk.ver" or sanName == "com.san.san-ex-sdk.ver":
            subLable.attrib[nameSpace + "value"] = sanValue


def getSanSdkInfo(new_package):
    if new_package.__contains__("gbwhatsapp"):  # gb
        return "6757e179-7b37-4902-a756-792898bbbbe3", "[3.8.3](383)"
    elif new_package.__contains__("obwhatsapp"):  # ob
        # TODO 替换
        return "6757e179-7b37-4902-a756-792898bbbbe3_ob", "[3.11.4](31104)_ob"
    elif new_package.__contains__("WhatsApp2Plus"):  # plus
        return "9aa604ef-3f90-42fb-985a-f32d17d5bee3", "[3.8.3](383)"
    elif new_package.__contains__("yowhatsapp"):  # yo
        return "510133b5-d994-47e2-b1b0-df68d7c2b2ac", "[3.6.4](364)"


def write_2_file(file_path, data_str):
    xml_data = f'<?xml version="1.0" encoding="utf-8" standalone="no"?>{data_str}'
    try:
        with codecs.open(file_path, mode='w+', encoding="utf-8") as f:
            f.write(xml_data)
    except Exception as result:
        print(f"写入{file_path}异常: {result}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("public_dir")
    args = parser.parse_args()
    public_dir = args.public_dir

    default_package = input(
        '请输入默认包名对应的数字：1->com.gbwhatsapp", "2->com.obwhatsapp", "3->com.WhatsApp2Plus", "4->com.yowhatsapp","5->其他包名"\n')
    if default_package.strip() == "5":
        user_default_package = input('请输入默认包名：\n')
        default_package_list.append(user_default_package.strip())

    new_package = input(
        '请输入新包名对应的数字：1->com.gbwhatsapp", "2->com.obwhatsapp", "3->com.WhatsApp2Plus", "4->com.yowhatsapp","5->其他包名"\n')
    if new_package.strip() == "5":
        user_new_package = input('请输入新包名：\n')
        new_package_list.append(user_new_package.strip())

    # 旧包默认index
    default_index = int(default_package) - 1
    # 新包默认index
    new_index = int(new_package) - 1
    replace_manifest(public_dir, default_package_list[default_index], new_package_list[new_index])
    print(f"替换AndroidManifest执行完毕，输出到：{public_dir}")
