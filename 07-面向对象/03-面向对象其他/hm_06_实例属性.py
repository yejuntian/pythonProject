class Dog(object):
    def __init__(self):
        self.age = 5

    def info_print(self):
        print(self.age)


wangcai = Dog()
print(wangcai.age)  # 5
# print(Dog.age) # 报错:实例例属性不不能通过类访问
wangcai.info_print()  # 5
