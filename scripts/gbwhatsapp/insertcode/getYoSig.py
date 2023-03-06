import argparse
import codecs
import os
import re

"""
    {
        "2.22.10.73": "LX/4Ne;",
        "method": [
            "getYoSig()[Landroid/content/pm/Signature;",
            "sec()Ljavax/crypto/SecretKey;",
            "md()[B"
        ],
        "string": "PkTwKSZqUfAUyR0rPQ8hYJ0wNsQQ3dW1+3SCnyTXIfEAxxS75FwkDf47wNv/c8pP3p0GXKR6OOQmhyERwx74fw1RYSU10I4r1gyBVDbRJ40pidjM41G1I1oN",
        "2.22.22.80": "LX/2Fq;",
        "id": "about_logo"
    }
"""

# 只匹配下面的文件类型
extends = ["smali"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'assets', 'kotlin',
             'lib', 'META-INF', 'original', 'res', 'unknown',
             'AndroidManifest.xml', 'apktool.yml', 'smali_classes5',
             'smali_classes6', 'smali_classes7']
# 用于存放查到的目标文件集合
find_file_list = []
targetStr = "[Landroid/content/pm/Signature;"
code1 = """
    invoke-static {{}}, Lcom/gbwhatsapp/yo/yo;->getYoSig()[Landroid/content/pm/Signature;

    move-result-object {register}
"""

code2 = """
    invoke-static {}, Lcom/gbwhatsapp/yo/yo;->getYoSig()[Landroid/content/pm/Signature;
    """


def find_file(from_dir, targetStr, file_list):
    """
    from_dir:目标目录
    targetStr：指定字符串
    file_list:用于存放查到的目标文件集合
    """
    listdir = os.listdir(from_dir)
    for filename in listdir:
        fpath = str(os.path.join(from_dir, filename))
        if filename not in blacklist:
            if os.path.isdir(fpath):
                find_file(fpath, targetStr, file_list)
            elif os.path.isfile(fpath):
                # 只extends的文件类型
                if fpath.split('.')[-1] in extends:
                    # print('fpath=', fpath)
                    with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
                        data = rf.read()
                        if data.__contains__(targetStr):
                            file_list.append(fpath)


def insert_code(file_list):
    # print(file_list)
    for fpath in file_list:
        enableWrite = False
        with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
            lines = list(map(lambda x: x.replace("\n", ""), rf.readlines()))
            for i in range(0, len(lines)):
                line = lines[i].strip()
                if not line.__contains__("Lcom/gbwhatsapp/yo/yo;->getYoSig()[Landroid/content/pm/Signature"):
                    if (line.startswith("sget-object") or line.startswith("iget-object")) and line.endswith(
                            "[Landroid/content/pm/Signature;"):
                        enableWrite = True
                        register = re.findall(r"[v,p]\d+", line)[0]
                        targetLine = lines[i + 1]
                        line = targetLine.replace(targetLine, code1.format(register=register))
                        lines[i + 1] = line
                    if line.startswith("invoke-static") and line.endswith("[Landroid/content/pm/Signature;"):
                        enableWrite = True
                        targetLine = lines[i + 1]
                        line = targetLine.replace(targetLine, code2)
                        lines[i + 1] = line

        if enableWrite:
            with open(fpath, 'w') as f:
                f.write("\n".join(lines))
                print("写入" + fpath)


def sign(from_dir):
    find_file(from_dir, targetStr, find_file_list)
    insert_code(find_file_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    sign(args.from_dir)
