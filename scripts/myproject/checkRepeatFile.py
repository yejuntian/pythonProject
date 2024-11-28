import re
import os

# 只匹配下面的文件类型
extends = ["smali", "xml"]
# 排除哪些文件夹
blacklist = ['.idea', '.git', 'build', 'lib', 'assets',
             'META-INF', 'original', 'res', 'unknown',
             'AndroidManifest.xml', 'apktool.yml']
# 所有文件路径列表
allFilePathList = []
# 重复文件路径列表
repeatFilePathList = []
regex = r"/(smali.*?)/(.*)"

"""
主要作用：检查项目中是否出现重复的文件路径，如果出现重复的文件路径则说明文件出现冲突，需要进行重命名操作。
        from_dir:项目地址
"""


def main(from_dir):
    checkRepeatFilePath(from_dir)
    if len(repeatFilePathList) > 0:
        print("**************重复的文件列表路径如下：**************")
        print(repeatFilePathList)
    print("**************程序执行结束**************")


def checkRepeatFilePath(from_dir):
    listdir = os.listdir(from_dir)
    for fname in listdir:
        fpath = os.path.join(from_dir, fname)
        if os.path.isdir(fpath):
            checkRepeatFilePath(fpath)
        elif os.path.isfile(fpath):
            if fpath.split('.')[-1] in extends:
                matches = re.finditer(regex, fpath, re.MULTILINE)
                for matchNum, match in enumerate(matches, start=1):
                    relativePath = match.group(2)
                    print(relativePath)
                    if relativePath not in allFilePathList:
                        allFilePathList.append(relativePath)
                    else:
                        repeatFilePathList.append(relativePath)


if __name__ == "__main__":
    from_dir = "/Users/tianyejun/work/Android/shareit/instapro_278.0.0.21.117/DecodeCode/instagram_278.0.0.21.117"
    main(from_dir)
