# 1. 定义类，定义类属性
class Dog(object):
    tooth = 10
    age =20


# 2. 创建对象
wangcai = Dog()
xiaohei = Dog()

# 3. 访问类属性： 类和对象
Dog.tooth = 30
print(Dog.tooth)
wangcai.tooth = 35
print(wangcai.tooth)
print(xiaohei.tooth)
