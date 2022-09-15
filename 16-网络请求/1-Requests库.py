import requests

# Requests库不是Python标准库，而是第三方开发的。 所以需要我们安装一下。
# 安装第三方库，前面的课程学过，使用包管理工具 pip。
# 执行命令 pip install requests 就可以了。

response = requests.get("http://mirrors.sohu.com/")
print(response.text)

# 使用Requests发送HTTP请求，url里面的参数，通常可以直接写在url里面
response = requests.get('https://www.baidu.com/s?wd=iphone&rsv_spt=1')
print(response.text)

# 字典对象传递给 Requests请求方法的 params 参数
urlParam = {
    "wd": "iphone",
    "rsv_spt": "1"
}

response = requests.get("https://www.baidu.com/s", params=urlParam)
print(response.status_code)

