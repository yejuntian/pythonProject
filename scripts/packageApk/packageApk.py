import codecs
import json
import argparse
import webbrowser

# 默认包名集合列表
default_package_list = ["com.gbwhatsapp", "com.obwhatsapp", "com.WhatsApp2Plus", "com.universe.messenger"]
# apk名称
appNameList = ["GBWhatsApp", "OBWhatsApp", "WhatsAppPlus"]
# app名称
appName = "GBWhatsApp"
# 配置url
baseUrl = "http://10.90.156.128:8080/job/gbwhatsapp/buildWithParameters?token=malinkang"
# 默认测试版本
defaultVersion = "2.23.15.501_test"
# 默认base版本
baseVersion = "2.23.15.81"


def packageApk():
    parser = argparse.ArgumentParser()
    parser.add_argument("configPath")
    args = parser.parse_args()
    configPath = args.configPath

    global appName
    packageNumber = input(
        '请输入包名对应的数字：1->com.gbwhatsapp", "2->com.obwhatsapp",'
        '"3->com.WhatsApp2Plus","4->com.universe.messenger"\n')
    packageName = default_package_list[int(packageNumber) - 1]

    if packageNumber == "4":
        appNameNumber = input(
            '请输入新包名对应的数字：1->GBWhatsApp", "2->OBWhatsApp","3->WhatsAppPlus"\n')
        appName = appNameList[int(appNameNumber) - 1]

    jsonData = loadData(configPath)
    sendUrl = f"{baseUrl}&AppName={appName}&PackageName={packageName}" \
              f"&VersionName={getNewStr(jsonData['versionName'])}" \
              f"&Changelog={getNewStr(jsonData['changelog'])}" \
              f"&&Base={baseVersion}"
    print(sendUrl)
    # 打开生成的URL链接
    webbrowser.open(sendUrl)


# 加载json数据
def loadData(fpath):
    with codecs.open(fpath, mode="r", encoding="utf-8") as rf:
        return json.loads(rf.read())


# 字符串拼接
def getNewStr(arr):
    if not arr:
        return defaultVersion
    new_string = "%0A".join(arr[:-1])
    if new_string:
        new_string += "%0A"  # 添加换行符，如果不为空
    new_string += arr[-1]  # 添加最后一个元素
    return new_string


if __name__ == '__main__':
    packageApk()
