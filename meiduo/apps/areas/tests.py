# def basedeco(func):
#     def wrapper():
#         print('上有天堂')
#         output = func()
#         print('下有苏杭')
#         return output
#
#     return wrapper
#
#
# @basedeco
# def testfun():
#     '''
#     这是一个测试函数
#     '''
#     print('我就是我，不一样的烟火')
#     print(testfun.__doc__)
#
#
# if __name__ == '__main__':
#     testfun()


# print("\n".join("\t".join(["%s*%s=%s" % (x, y, x * y) for y in range(1, x + 1)]) for x in range(1, 10)))

# wife = ['diaoqian', 1988, ['slaras', 10000]]
# hasband = wife[:]
#
# hasband[0] = 'zhaoyun'
# hasband[2][1] = 2000
# print(hasband)
# print(wife)

# print(15 / 5)

# def basefunck(func):
#     def nextfunc():
#         print('this is next func')
#     return nextfunc
#
# @basefunck
# def a():
#     print('this is a_func')
#
# a()

# 例子：
#
# 业务函数：
def f1():
    print('f1')

def f2():
    print('f2')

def f3():
    print('f3')


# 装饰器
def super_f(fun):
    def inner():
        # 新增功能
        print('add func in here')
        return fun()
    return inner
# 把原来的业务函数塞进装饰器中的内嵌函数，再返回一个新的功能完善的函数
# 装饰器的使用

@super_f
def f1():
    print('f1')

f1()