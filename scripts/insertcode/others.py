import Utils
from CommonInsert import *


# 获取x()所需参数
def getXParam(matches, lines, num, rowOffSet):
    for match in matches:
        line = match.group(1)
        param = match.group(2)
        return line, param


# 获取需要替换为x()所在行
paramStr = getParam(
    "This Activity already has an action bar supplied by the window decor. Do not request Window.FEATURE_SUPPORT_ACTION_BAR and set windowActionBar to false in your theme to use a Toolbar instead.",
    regexList=[
        "invoke\-virtual \{.*\}\, (.*\-\>(.*)LX\/.*)",
        "move\-result\-object v\d",
        "invoke\-virtual \{.*\}\, Landroid\/app\/Activity\;\-\>getWindow\(\)Landroid\/view\/Window\;"
    ]
    , func=getXParam)

# 替换为x()需要排除的class
allExcludeFileList = [
    "smali_classes2/com/gbwhatsapp/chatinfo/ContactInfoActivity.smali",
    "smali_classes2/com/gbwhatsapp/gallerypicker/MediaPicker.smali",
    "smali_classes2/com/gbwhatsapp/mediaview/MediaViewBaseFragment.smali",
    "smali_classes2/com/gbwhatsapp/profile/ViewProfilePhoto.smali"
]
excludeFileList = findXByStr("dialogtoast/update-progress-message/dialog-type-not-progress-dialog/ \\\"")
allExcludeFileList.extend(excludeFileList)

homeActivityTabActive_color_id = getPublicIdByName("homeActivityTabActive", "color")


# 格式化参数
def modContPick(codeStr, match, hasParam):
    if paramStr[1] != "x()":
        return codeStr.format(param=paramStr[1])
    else:
        return None


def getXFormatCode(codeStr, match, hasParam):
    param1 = match.group(1)
    param2 = match.group(2)
    if param1 is not None and param2 is not None:
        param2 = param2.replace(paramStr[1], "x()")
        return codeStr.format(param1=param1, param2=param2)
    return None


def others():
    return [
        CommonInsert(filePathList=Utils.findFileByName("ContactPickerFragment"),
                     codeFilePath="smali/others/MainBKC",
                     regexList=[
                         ["const v\d+, 0x102000a",
                          matchLine,
                          "move\-result\-object v\d+",
                          "check\-cast (v\d+)\, Landroid\/widget\/ListView\;"
                          ]
                     ],
                     rowOffSet=0),

        CommonInsert(filePathList=getTransFileList(paramStr[0], allExcludeFileList),
                     codeFilePath="smali/others/x",
                     regexList=[r"invoke\-virtual \{(.*)\}\, " + f"({re.escape(paramStr[0])})"],
                     rowOffSet=0,
                     code=getXFormatCode),

        CommonInsert(filePathList=Utils.findXByStr(
            "This Activity already has an action bar supplied by the window decor. Do not request Window.FEATURE_SUPPORT_ACTION_BAR and set windowActionBar to false in your theme to use a Toolbar instead."),
            codeFilePath="smali/others/modContPick",
            rowOffSet=insertFileEnd,
            code=modContPick),

        CommonInsert(filePathList=findFileByName("HomeActivity"),
                     codeFilePath="smali/others/actionbarbk",
                     regexList=[
                         ["\.locals 4",
                          matchLine,
                          matchLine,
                          matchLine,
                          matchLine,
                          matchLine,
                          "if\-nez \w+\, \:cond_\d+",
                          "new\-instance v\d+\, Landroid\/animation\/ValueAnimator\;"
                          ],
                         ["if\-nez v\d+\, \:cond_\d+",
                          "const\-string\/jumbo v\d+\, \"search_fragment\""
                          ]
                     ],
                     rowOffSet=-2,
                     hasParam=False),

        CommonInsert(filePathList=findFileByName("Conversation"),
                     codeFilePath="smali/others/actionbarbk",
                     regexList=["\.method public onSearchRequested\(\)Z"],
                     rowOffSet=8,
                     hasParam=False),

        CommonInsert(filePathList=findXByStr("conversation/dialog/delete no messages"),
                     codeFilePath="smali/others/actionbarbk",
                     regexList=["check\-cast v\d+\, Landroid\/app\/Activity\;"],
                     rowOffSet=1,
                     hasParam=False),

        CommonInsert(
            filePathList=findXByStr("MessageAddOnManager/getLastChatsListCachedDisplayedMessageAddOnV2/no chat for "),
            codeFilePath="smali/others/getHomeCounterBKColor",
            regexList=[
                ["move\-result (\w+)",
                 matchLine,
                 matchLine,
                 "invoke\-virtual \{v\d+\, v\d+\}\, Landroid\/view\/View\;\-\>setBackground\(Landroid\/graphics\/drawable\/Drawable\;\)V"
                 ]
            ],
            rowOffSet=-8),

        CommonInsert(
            filePathList=findFileByName("HomeActivity"),
            codeFilePath="smali/others/getTabBageBKColor",
            regexList=[
                [
                    f"const \w+\, {re.escape(homeActivityTabActive_color_id)}",
                    "\:cond_\w+",
                    "invoke\-static .*",
                    "move\-result (\w+)",
                    "new\-instance .*"
                ]
            ],
            rowOffSet=2),

    ]


if __name__ == "__main__":
    objectList = others()
    for entity in objectList:
        entity.insertCode()
