from Utils import *

# 插入到文件末尾
insertFileEnd = -100
# 匹配任意一行正则
matchLine = r"^.*$"


class CommonInsert:
    def defaultFormatCode(codeStr, match, hasParam):
        if hasParam:
            if match is None:
                return codeStr
            params = match.group(1)
            if params is not None:
                return codeStr.format(param=params)
            return None
        else:
            return codeStr

    def __init__(self, filePathList, codeFilePath, regexList=None, rowOffSet=1, code=defaultFormatCode, hasParam=True,
                 exitTotalCount=1):
        """
            filePathList：扫描的结果，返回文件path列表
            insertCodeFilePath：代码存储的文件路径
            regexList：正则列表；(既可以匹配单行，也可以匹配多行)
            rowOffSet：行偏移
            code：多参param需要子类实现
            hasParam：是否有参数
            totalCount：当前类中存在的个数
        """
        self.filePathList = filePathList
        self.codeFilePath = codeFilePath
        self.regexList = regexList
        self.rowOffSet = rowOffSet
        self.code = code
        self.hasParam = hasParam
        self.exitTotalCount = exitTotalCount

    def insertCode(self):
        count = 0
        for fpath in self.filePathList:
            if insertFileEnd == self.rowOffSet:
                self.insertFileEnd(fpath)
            else:
                self.writeCode(fpath, count)

    # 插入代码到末尾
    def insertFileEnd(self, fpath):
        isWrite = False
        with codecs.open(fpath, "r", "utf-8") as rf:
            data = rf.read()
            code = self.code(getFileData(self.codeFilePath), None)
        with codecs.open(fpath, "a", "utf-8") as wf:
            if code is not None and code not in data:
                print(f"*********** 正在插入代码{self.codeFilePath} ****************")
                isWrite = True
                wf.write(code)
            else:
                print(f"*********** 已存在代码{self.codeFilePath} {newPath} ****************")
            if isWrite:
                print(f"*********** 插入代码 {self.codeFilePath} 完成****************")
            # 添加没有插入的类
            pass

    def writeCode(self, fpath, count):
        newPath = fpath[len(newProjectPath) + 1:]
        isWrite = False
        with codecs.open(fpath, "r", "utf-8") as rf:
            lines = rf.readlines()
            data = "".join(lines)
            if len(self.regexList) == 1:
                for num in range(0, len(lines)):
                    matches = re.finditer(self.regexList[0], lines[num], re.MULTILINE)
                    for match in matches:
                        code = self.code(getFileData(self.codeFilePath), match, self.hasParam)
                        if code is not None:
                            count += 1
                            if code not in data:
                                isWrite = True
                                lines[num + self.rowOffSet] = code
            else:
                matches = re.finditer(self.getMultilineRegex(), data, re.MULTILINE)
                for match in matches:
                    last_match_end = match.end()
                    num = data.count('\n', 0, last_match_end) - 1
                    code = self.code(getFileData(self.codeFilePath), match, self.hasParam)
                    if code is not None:
                        count += 1
                        if code not in data:
                            isWrite = True
                            lines[num + self.rowOffSet] = code
            if code is not None:
                if code not in data:
                    pass
                else:
                    print(f"*********** 已存在代码{self.codeFilePath} {newPath} 共有{count}处 ****************")
                if count > 0:
                    print(f"*********** 插入代码{self.codeFilePath} {newPath} 共有{count}处 ****************")

        with codecs.open(fpath, "w", "utf-8") as wf:
            if self.code is not None:
                wf.write("".join(lines))
                if isWrite:
                    print(f"*********** 插入代码 {self.codeFilePath} 完成****************")
                else:
                    # 添加没有插入的类
                    pass

    # 匹配多行正则
    def getMultilineRegex(self):
        regexStr = ""
        for str in self.regexList:
            regexStr += (str + r"\n^\s*")
        return regexStr
