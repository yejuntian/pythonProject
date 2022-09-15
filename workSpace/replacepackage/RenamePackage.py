import codecs
import glob
import os
import shutil
import ParseManifest

# 替换的键值对，一行两个字符串，前面的是旧字符串，后面的是新字符串，中间用空格隔开
key_path = 'replacekeys.properties'
# 待替换文件的 文件夹目录，会递归检索文件，并替换文件中所有的字符串
folder_path = r"../DecodeCode/YoWhatsApp_v17"
# 只匹配下面的文件类型
extends = ['smali', 'xml']
# 排除哪些文件夹
blacklist = ['.idea', 'build', 'assets', 'build', 'lib', 'META-INF', 'original',
             'AndroidManifest.xml',
             'apktool.yml']
# 默认包名
defaultPackage = "com.gbwhatsapp"
# 新包名
newPackage = "com.yowhatsapp"


def load_replace_keys(key_path):
    mapping_string = []
    with codecs.open(key_path, "r", "utf-8") as rfile:
        for line in rfile.readlines():
            if line.find("=") != -1:
                line = line[0:line.find('#')]
            if line.find('=') > 0:
                strs = line.split("=")
                mapping_string.append([strs[0].strip(), strs[1].strip()])
    return mapping_string


def excuepath(folder_path, blacklist, extends):
    os.chdir(folder_path)
    cwd = os.getcwd()
    dirs = os.listdir(cwd)
    for tmp in dirs:
        # 排除blacklist文件夹
        if tmp not in blacklist:
            fpath = os.path.join(cwd, tmp)
            if os.path.isfile(fpath):
                print('fpath=', fpath)
                # 只extends的文件类型
                if fpath.split('.')[-1] in extends:
                    with codecs.open(fpath, "r", "utf-8") as rfile:
                        data = rfile.read()
                    with codecs.open(fpath, "w", "utf-8") as wfile:
                        replace_times = 0
                        for item in mapping_string:
                            replace_times += data.count(item[0])
                            data = data.replace(item[0], item[1])
                        print(r'替换次数：', replace_times)
                        wfile.write(data)
            # 如果是文件夹，递归
            elif os.path.isdir(fpath):
                excuepath(fpath, blacklist, extends)


def renameDirectory(oldFolderName, newFolderName):
    curPath = os.getcwd()
    pos = curPath.rfind(r"smali")
    curPath = curPath[:pos]
    print(f"curPath = {curPath}")
    os.chdir(curPath)
    fileList = glob.glob(curPath + "/" + "smali*/com/*")
    print(fileList)
    for file in fileList:
        if file.rfind("/") > 0:
            dirName = file[file.rindex("/")+1:]
            print(f"dirName = {dirName}")
            if dirName == oldFolderName:
                newDir = file.replace(oldFolderName,newFolderName)
                os.rename(file, newDir)


if __name__ == '__main__':
    mapping_string = load_replace_keys(key_path)
    print(mapping_string)
    ParseManifest.parseAndroidManifestXml(oldPackage=defaultPackage, newPackage=newPackage)
    excuepath(folder_path, blacklist, extends)
    renameDirectory("gbwhatsapp", "yowhatsapp")
