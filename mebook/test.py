#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import re

apps = [1, 2, 3, 4]
myIters = iter(apps)


def printff(str):
    print("str = ", str)


def test():
    print("start...")
    for app in apps:
        yield printff(app)


# def test2():
#     temp = next(myIters)
#     while temp != StopIteration:
#         print(temp)
#         temp = next(myIters)

test()
