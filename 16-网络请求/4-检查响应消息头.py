import requests,pprint

# 要检查 HTTP 响应 的消息头，直接 通过 reponse对象的 headers 属性获取
response = requests.get('http://mirrors.sohu.com/')
print(response.headers)
pprint.pprint(dict(response.headers))