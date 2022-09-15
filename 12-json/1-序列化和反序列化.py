import json

historyTransactions = [

    {
        'time': '20170101070311',  # 交易时间
        'amount': '3088',  # 交易金额
        'productid': '45454455555',  # 货号
        'productname': 'iphone7'  # 货名
    },
    {
        'time': '20170101050311',  # 交易时间
        'amount': '18',  # 交易金额
        'productid': '453455772955',  # 货号
        'productname': '奥妙洗衣液'  # 货名
    }

]
# 序列化为json格式的字符串就可以使用该库里面的dumps函数

# json.dumps 方法发现将字符串中如果有非ascii码字符
# indent参数表示转换后缩进为4，这样显得整洁好看
jsonStr = json.dumps(historyTransactions, ensure_ascii=False, indent=3)
print(jsonStr)

#  把json字符串反序列化为数据对象
# 2.把json格式的字符串变为Python中的数据对象

jsonstr = '[{"time": "20170101070311", "amount": "3088", "productid": "45454455555", "productname": "iphone7"}, {"time": "20170101050311", "amount": "18", "productid": "453455772955", "productname": "\u5965\u5999\u6d17\u8863\u6db2"}]'
transList = json.loads(jsonstr)
print(transList)
