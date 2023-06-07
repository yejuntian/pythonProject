import codecs
import json
import os
import re

# radioButton3.setText(yo.getString("no_internet_title") + " (\"" + yo.getString("voip_call_outgoing") + "\")👻")
regex1 = r"yo.getString\(\".*\"\)"
# yo.getString(z5 ? "disableFingerprintFirst" : "fingerprint_setup_dialog_title")
regex2 = r"yo.getString\(.+ ? : \".*\"\)"
# a.j("register_try_again_later", yo.getCtx(), 0);
regex3 = r"a.j\(\".+\""
# yo.getID(LockUtils.isJIDLocked(yo.getCurr_sJid()) ? "unlock" : "lock","string")
regex4 = r"yo.getID\(.*, *?\"string\"\)"
# 正则匹配集合
reList = [regex1, regex2, regex3, regex4]

# 匹配()括号内容
regex = r"\"[\w_]+\""
# 排除哪些文件夹
blacklist = ['.idea', '.git', '.gradle', 'kotlin', 'lib', 'META-INF',
             'original', 'AndroidManifest.xml', 'apktool.yml']
# 只匹配下面的文件类型
extends = ["java"]
strList = set()


def transFolder(from_dir, black_list):
    from_listdir = os.listdir(from_dir)
    for file_name in from_listdir:
        from_file_path = os.path.join(from_dir, file_name)
        if file_name not in black_list:
            if os.path.isdir(from_file_path):
                transFolder(from_file_path, black_list)
            elif os.path.isfile(from_file_path):
                if file_name.split('.')[-1] in extends:
                    # print(from_file_path)
                    with codecs.open(from_file_path, "r", "utf-8") as rf:
                        data = rf.read()
                        for reg in reList:
                            matchesRegex(reg, data)


def matchesRegex(reg, data):
    matches = re.finditer(reg, data, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        groupStr = match.group()
        print(groupStr)
        matches = re.finditer(regex, groupStr, re.MULTILINE)
        for subMatchNum, subMatch in enumerate(matches, start=1):
            subGroupStr = subMatch.group()
            if not subGroupStr == '"string"':
                strList.add(subGroupStr)
                # print(subGroupStr)


def save_2_file(dataList, fileName):
    list = []
    for item in dataList:
        str = item.replace('"', '').strip()
        if not str in list:
            list.append(str)
    jsonStr = json.dumps(list, ensure_ascii=False, indent=2)
    with open(fileName, "w+") as wf:
        wf.write(jsonStr)
    print(f"结果保存到：{os.path.join(os.getcwd(), fileName)}")


if __name__ == "__main__":
    from_dir = "/Users/shareit/work/GBWorke/WhatsAppPlus_origin_java"
    transFolder(from_dir, blacklist)
    save_2_file(strList, "string_list.json")
