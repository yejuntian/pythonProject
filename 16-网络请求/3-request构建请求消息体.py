import requests
import json

# XML 格式消息体
payload = '''
<?xml version="1.0" encoding="UTF-8"?>
<WorkReport>
    <Overall>良好</Overall>
    <Progress>30%</Progress>
    <Problems>暂无</Problems>
</WorkReport>
'''

response = requests.post("http://httpbin.org/post", data=payload.encode("utf8"))
print(response.text)

# urlencoded 格式消息体

# 这种格式的消息体就是一种 键值对的格式存放数据，如下所示
# key1=value1&key2=value2

payload = {'key1': 'value1', 'key2': 'value2'}
r = requests.post("http://httpbin.org/post", data=payload)
print(r.text)

# json 格式消息体
payload = {
    "Overall": "良好",
    "Progress": "30%",
    "Problems": [
        {
            "No": 1,
            "desc": "问题1...."
        },
        {
            "No": 2,
            "desc": "问题2...."
        },
    ]
}
response = requests.post("http://httpbin.org/post", data=json.dumps(payload))
print(response.status_code)

# 也可以将 数据对象 直接 传递给post方法的 json参数，如下
response = requests.post("http://httpbin.org/post", json=payload)
print(response)
