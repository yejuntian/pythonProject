import codecs
import glob
import re
import argparse

targetStr = "gdrive-new-user-setup/create no need to display GoogleDriveNewUserSetupActivity, exiting."
code = """
    const/4 {param}, 0x0
    """

"""
    主要作用：关闭谷歌云备份
"""


def closeCloudBackUp(from_dir):
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
    closeCloudBackUp(from_dir)
