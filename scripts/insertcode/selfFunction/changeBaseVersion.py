from scripts.insertcode.CommonInsert import *

"""
  主要作用：修改WhatsApp基础版本号
"""

versionCode = getParam(
    "WhatsAppLibLoader",
    regexList=["const\-string v\d\, \"whatsapplibloader\/usable jniVersion\: \""],
    rowOffSet=12,
    matchRex=r"const\-string v\d\, (.*)",
    isFindX=False)

# baseLongVer = getParam(
#     "ProfiloUploadService",
#     regexList=[
#         ["const\-string .*\, \"build_id\"",
#          "const\-wide\/32 \w+\, (.*)"
#          ]
#     ],
#     isFindX=False
# )
baseLongVer = "0x22ee6f74"


# 获取版本号参数
def getVersionCode():
    if versionCode is None:
        return versionCode
    else:
        return fr"const\-string (.*)\, {re.escape(versionCode)}"


# 获取build_id
def getBaseLongVer():
    if baseLongVer is None:
        return baseLongVer
    else:
        return fr"const\-wide\/32 (\w+)\, {re.escape(baseLongVer)}"


def changeWAVersion():
    return [
        CommonInsert(filePathList=getTransFileList(getVersionCode(), []),
                     codeFilePath="smali/Utils/getBaseStrVer",
                     regexList=[getVersionCode()],
                     rowOffSet=0, ),
        CommonInsert(filePathList=findFileByName("WhatsAppLibLoader"),
                     codeFilePath="smali/Utils/getBaseStrVer",
                     regexList=[
                         [
                             "invoke\-static \{\}\, Lcom\/whatsapp\/nativelibloader\/WhatsAppLibLoader\;\-\>getJNICodeVersion\(\)Ljava\/lang\/String\;",
                             "move\-result\-object (.*)"
                         ]
                     ],
                     rowOffSet=-1,
                     ),
        CommonInsert(filePathList=getTransFileList(getBaseLongVer(), []),
                     codeFilePath="smali/Utils/getBaseLongVer",
                     regexList=[getBaseLongVer()],
                     rowOffSet=0, ),
    ]


if __name__ == "__main__":
    objectList = changeWAVersion()
    for entity in objectList:
        entity.insertCode()

    # print(getVersionCode())
