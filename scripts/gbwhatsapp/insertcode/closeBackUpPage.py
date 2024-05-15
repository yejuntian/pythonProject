import codecs
import glob
import re
import argparse

# 关闭备份页面code
targetStr = "gdrive-new-user-setup/create no need to display GoogleDriveNewUserSetupActivity, exiting."
code = """
    const/4 {param}, 0x0
    """
# 关闭备份弹框code2
targetStr2 = "com.google.android.gms.availability"
regexStr = "\.method public static final A\d+\(Landroid\/content\/Context\;Landroid\/content\/DialogInterface\$OnCancelListener\;LX\/\w+\;I\)Landroid\/app\/AlertDialog\;"
code2 = """    const/4 v0, 0x0
    
    return-object v0"""
"""
    主要作用：关闭跳转到谷歌定期备份页面
"""


def closeBackUp(from_dir):
    # 关闭备份页面
    closeCloudBackUpPage(from_dir)
    # 关闭备份对话框
    closeBackUpAlertWindow(from_dir)


def closeBackUpAlertWindow(from_dir):
    fpath = getXFilePath(from_dir, regexStr)
    print(fpath)
    if fpath is not None:
        with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
            lines = list(map(lambda x: x.replace("\n", ""), rf.readlines()))
            for i in range(0, len(lines)):
                line = lines[i].strip()
                if re.search(regexStr, line):
                    enableWrite = True
                    targetLine = i + 3
                    lines[targetLine] = code2
        if enableWrite:
            with codecs.open(fpath, 'w', "utf-8") as wf:
                wf.write("\n".join(lines))
                print("写入" + fpath)


# 根据regex查找文件路径
def getXFilePath(from_dir, regex):
    filePathList = glob.glob(from_dir + "/smali*/X/*.smali", recursive=True)
    for fpath in filePathList:
        with codecs.open(fpath, "r", 'utf-8') as rf:
            data = rf.read()
            if re.search(regex, data, re.MULTILINE):
                return fpath


def closeCloudBackUpPage(from_dir):
    fileList = glob.glob(f"{from_dir}/**/com/gbwhatsapp/**/**/GoogleDriveNewUserSetupActivity.smali")
    for fpath in fileList:
        enableWrite = False
        with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
            lines = list(map(lambda x: x.replace("\n", ""), rf.readlines()))
            for i in range(0, len(lines)):
                line = lines[i].strip()
                if line.__contains__(targetStr):
                    enableWrite = True
                    paramLine = i - 2
                    param = re.findall(r"[v,p]\d+", lines[paramLine])[0]
                    targetLine = lines[paramLine - 1]
                    line = targetLine.replace(targetLine, code.format(param=param))
                    lines[paramLine - 1] = line
        if enableWrite:
            with codecs.open(fpath, 'w') as f:
                f.write("\n".join(lines))
                print("写入" + fpath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("from_dir")
    args = parser.parse_args()
    from_dir = args.from_dir
    # from_dir = "/Users/shareit/work/shareit/gbwhatsapp/DecodeCode/whatsapp_1"
    closeBackUp(from_dir)
