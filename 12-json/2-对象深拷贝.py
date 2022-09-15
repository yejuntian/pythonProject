import json

team1 = [
    {
        'name': '乔丹',
        'height': 198
    },
    {
        'name': '姚明',
        'height': 228
    }

]
# 序列化为json字符串
dumps = json.dumps(team1)
# 反序列化为数据对象
team2 = json.loads(dumps)
team2[0]["name"] = "张三"

print(team1)
print(team2)
