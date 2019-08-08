import re
import os, os.path
import shutil
import random
import string
import datetime
from operator import itemgetter, attrgetter

intab = '\/:*?"<>|'
outtab = "  ： ？“《》 "  # 用于替换特殊字符

# 替换不能用作文件名的字符
def changechar(s):
    return s.translate(str.maketrans(intab, outtab))


def getTimeShow(s):  # 获取显示的时间 '添加于 2018年11月18日星期日 下午10:42:13'
    matchObj = re.match(r"添加于 (.*)年(.*)月(.*)日星期(.*)", s, re.M | re.I)  # 2018.11.18
    retStr = matchObj.group(1) + "." + matchObj.group(2) + "." + matchObj.group(3)
    return retStr


def getBeginPos(s):  # 您在位置 #271-274的标注 //您在位置 #1602 的笔记
    matchObj = re.match(r"(.*)#(.*)-(.*)的标注(.*)", s, re.M | re.I)  # 的笔记
    matchObj2 = re.match(r"(.*)#(.*) 的笔记(.*)", s, re.M | re.I)  # 的笔记
    retStr = "0"
    if matchObj:
        retStr = matchObj.group(2)
    if matchObj2:
        retStr = matchObj2.group(2)
    return int(retStr)


def getAddr(s):  # 获取标注位置
    g = s.split(" | ")[0]
    return g


def getTime(s):  # 获取添加时间
    g = s.split(" | ")[1]
    return g.split("\n\n")[0]


def getMark(s):  # 获取标注内容
    g = s.split(" | ")[1]
    try:
        return g.split("\n\n")[1]
    except IndexError:
        # print("list index out of range due to empty content")
        return "empty content"
