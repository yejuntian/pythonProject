# 1. 定义类：私有类属性，类方法获取这个私有类属性
class Dog(object):
    __tooth = 10
    name = "zhangsan"

    def __init__(self):
        age = 30

    # 定义类方法
    @classmethod
    def get_tooth(cls):
        cls.age = 20
        print(cls.age)
        return cls.__tooth

    def get_tooth2(self):
        return self.__tooth

    @staticmethod
    def get_tooth3(name):
        return name


# 1.调用类方法
print(Dog.get_tooth())

# 2. 创建对象，调用类方法
wangcai = Dog()
print(wangcai.get_tooth2())
