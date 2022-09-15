import requests

# Requests发送这样的数据，只需要将这些键值对的数据填入一个字典
# 然后使用post方法的时候，指定参数 headers 的值为这个字典就可以

header = {
    "user-agent": "my-app/0.0.1",
    "auth-type": "jwt-token"
}

response = requests.post("http://httpbin.org/post", headers=header)
print(response.status_code)



