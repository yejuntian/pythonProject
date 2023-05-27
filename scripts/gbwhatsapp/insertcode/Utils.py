import re
import glob
import codecs


# 根据regex查找文件路径
def getXFilePath(from_dir, regex):
    filePathList = glob.glob(from_dir + "/smali*/X/*.smali", recursive=True)
    for fpath in filePathList:
        with codecs.open(fpath, "r", 'utf-8') as rf:
            data = rf.read()
            if re.search(regex, data, re.MULTILINE):
                return fpath
