import shutil

# 如果我们要拷贝一个目录里面所有的内容（包括子目录和文件、子目录里面的子目录和文件，等等）到另外一个目录中

# 注意拷贝前， 目标目录必须 不存在 ，否则会报错。
#
# 上面的代码执行前面，如果 e:/new/bbb 已经存在，执行到copytree时，就会报错
#
# 上面的代码执行前面，如果 e:/new 这个目录都不存在，执行到copytree时，就会 创建 e:/new 目录，再创建 e:/new/bbb 目录，再拷贝 d:/tools/aaa 目录中所有的内容 到 e:/new/bbb 中。
#
# 上面的代码执行前面，如果 e:/new 这个目录存在，但是 e:/new/bbb 不存在，执行到copytree时，就只会 创建 e:/new/bbb ，再拷贝 d:/tools/aaa 目录中所有的内容 到 e:/new/bbb 中。

shutil.copytree('../test', "../testCopy/copy")
