import Utils
from CommonInsert import *


def stories():
    return [
        CommonInsert(filePathList=Utils.findFileByName("ContactStatusThumbnail"),
                     codeFilePath="smali/Stories/method",
                     rowOffSet=insertFileEnd),
        CommonInsert(filePathList=Utils.findFileByName("ContactStatusThumbnail"),
                     codeFilePath="smali/Stories/line",
                     regexList=["iget (v\w+)\, p0\, Lcom\/gbwhatsapp\/status\/ContactStatusThumbnail\;\-\>A00\:I"]),
        CommonInsert(filePathList=Utils.findFileByName("ContactStatusThumbnail"),
                     codeFilePath="smali/Stories/seenColor",
                     regexList=["const\/4 v\w+\, 0x0",
                                "invoke\-virtual .*\, Landroid\/content\/res\/TypedArray\;\-\>getInteger\(II\)I",
                                "move\-result (v\w+)"],
                     rowOffSet=0),
        CommonInsert(filePathList=Utils.findFileByName("ContactStatusThumbnail"),
                     codeFilePath="smali/Stories/unseenColor",
                     regexList=["const\/4 v\w+\, 0x2",
                                "invoke\-virtual .*\, Landroid\/content\/res\/TypedArray\;\-\>getInteger\(II\)I",
                                "move\-result (v\w+)"],
                     rowOffSet=0)
    ]


if __name__ == "__main__":
    for entity in stories():
        entity.insertCode()
