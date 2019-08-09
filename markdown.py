#!/usr/local/bin/python3
# coding=utf-8
import re
import os, os.path
import shutil
import random
import string
import datetime
import threading
from operator import itemgetter, attrgetter
import sys

sys.path.append("libs/")

import util
import book
import config1

lock = threading.RLock()  # 操作allBooks的锁

inputFile = "source.txt"
inputFile = "My Clippings.txt"
nowTime = datetime.datetime.now().strftime("_%Y-%m-%d")  # 现在
# print("nowTime = ", nowTime)

allBooks = config1.allBooks

TEMP_FOLDER = "out"  # 临时文件夹
FILE_SUFFIX = nowTime + ".markdown"  # 文件后缀名
FILE_COUNT_SENTENCE = "FILE_COUNT_SENTENCE"  # 文件总条数
BEGAN_TIME = "BEGAN_TIME"  # 开始时间
END_TIME = "END_TIME"  # 结束时间

# 初始化函数
# 分割函数实现利用关键词进行简单的分割成列表
# 结果为每一条单独的笔记，包含书名，时间，位置和内容
def init():
    BOUNDARY = u"==========\n"  # 分隔符
    f = open(inputFile, "r", encoding="utf-8")
    content = f.read()  # 读取全部内容
    content = content.replace(u"\ufeff", u"")  # 替换书名前的空格
    clips = content.split(BOUNDARY)
    print("列表个数：", clips.__len__())  # 获取列表的个数
    return clips


def initDir():
    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
    os.mkdir(TEMP_FOLDER)  # 创建一个books目录，用于存放书名网页文件
    os.chdir(TEMP_FOLDER)  # 更改工作目录


both = []  # 完整内容。格式为[['',''],['','']……]
books = []  # 书名列表
sentence = []  # 标注内容
# 获取书名存储为列表books，获取除书名外的内容为sentence
def initContents():
    clips = init()
    sum = clips.__len__()
    for i in range(0, sum):
        book = clips[i].split("\n-")
        both.append(book)
        # print(book)
        if book != [""]:  # 如果书名非空
            books.append(util.changechar(book[0]))  # 添加书名，替换特殊字符，以便创建文件
            sentence.append(book[1])  # 添加笔记


initContents()
initDir()
print("笔记总数：", sentence.__len__())

# 去除书名列表中的重复元素
nameOfBooks = list(set(books))
nameOfBooks.sort(key=books.index)
print("书籍总数：", nameOfBooks.__len__())
# print(nameOfBooks)

# 根据不同书名建立网页文件
stceOfBookCnt = {}  # 记录每本书有几条标注的字典
# print(os.listdir())


def findBook(name, inputI):
    found = book.BookInfo(name, [], [])
    for curBook in inputI:
        if name.startswith(curBook.name):
            curBook.name = name
            found = curBook
            break
    return found


for j in range(0, nameOfBooks.__len__()):
    # 网页文件的字符长度不能太长，以免无法在linux下创建
    if nameOfBooks[j].__len__() > 80:
        nameOfBooks[j] = nameOfBooks[j][0:80]  # 截取字符串

    curBook = findBook(nameOfBooks[j], allBooks)
    for ccBook in allBooks:
        if ccBook.name == curBook.name:
            break
        else:
            allBooks.append(curBook)
            break
    print("ccc = ", curBook.name)
    curBook.fileName = nameOfBooks[j] + FILE_SUFFIX
    stceOfBookCnt[curBook.fileName] = 0

    header = "# " + nameOfBooks[j] + "\n\n"  # 写入书名
    header = header + "  " + "共 `" + FILE_COUNT_SENTENCE + "` 条标注" + " , "  # 临时评论数目
    header = header + "`" + BEGAN_TIME + "--" + END_TIME + "`"
    header = header + "\n\n\n"
    curBook.header = header

# 向文件添加标注内容
stce_succ_cnt = 0  # 向html文件添加笔记成功次数
stce_fail_cnt = 0  # 向html文件添加笔记失败次数
# print("html name:",os.listdir())
file_list = os.listdir(".")  # 获取当前目录文件名，存放于file_list
for j in range(0, sentence.__len__()):
    temp = both[j]
    filename = util.changechar(temp[0][0:80]) + FILE_SUFFIX
    curBook = findBook(filename, allBooks)
    s1 = util.getAddr(temp[1])  # 获取标注位置
    s2 = util.getTime(temp[1])  # 获取标注时间
    s3 = util.getMark(temp[1])  # 获取标注内容
    if s3 != "\n":  # 如果文本内容非空
        stce_succ_cnt += 1
        cnt_temp = stceOfBookCnt[filename]
        stceOfBookCnt[filename] = cnt_temp + 1
        # senContent = "\n### " + str(cnt_temp + 1) + ". " + s3
        senContent = s3
        senContent = senContent + "\n    " + s2 + " &&" + s1 + "\n"
        senContent = senContent + "\n"
        curSen = book.Sentence(senContent, util.getBeginPos(s1))
        if curBook.hasChapter:
            curBook.appendChapterSen(curSen)
        else:
            curBook.appendSen(curSen)
        if curBook.sentenceLen() == 1:
            curBook.beginTime = util.getTimeShow(s2)
    else:
        stce_fail_cnt += 1
        print("empty txt", stce_fail_cnt, filename)
    curBook.endTime = util.getTimeShow(s2)

print("sentence add succ cnt = ", stce_succ_cnt)
print("sentence add fail cnt = ", stce_fail_cnt)
print("allBooks length = ", len(allBooks))
# 添加总条数信息
for curBook in allBooks:
    fileName = curBook.fileName
    # print("fileName=", fileName)
    f = open(fileName, "w+", encoding="utf-8")  # 打开对应的文件
    header = curBook.header
    header = header.replace(FILE_COUNT_SENTENCE, str(curBook.sentenceLen()))
    header = header.replace(BEGAN_TIME, curBook.beginTime)
    header = header.replace(END_TIME, curBook.endTime)
    f.write(header)

    if curBook.hasChapter:
        for chapter in curBook.chapters:
            chapter.sortSen()
            f.write("## " + chapter.name + "\n\n")
            f.write("  **本章共`" + str(len(chapter.sentences)) + "`条标注**\n\n")
            for index, sen in enumerate(chapter.sentences):
                f.write("#### " + str(index + 1) + ". " + sen.content + "")
    else:
        for index, sen in enumerate(curBook.sentences):
            f.write("#### " + str(index + 1) + ". " + sen.content + "")

    f.write("文件生成时间: " + str(datetime.datetime.now()))
    f.close()

