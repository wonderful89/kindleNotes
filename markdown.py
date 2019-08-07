#coding=utf-8
import re
import os,os.path
import shutil
import random
import string
import datetime

nowTime=datetime.datetime.now().strftime('_%Y-%m-%d')#现在
print('nowTime = ', nowTime)

TEMP_FOLDER = "out" # 临时文件夹
FILE_SUFFIX = nowTime+".markdown" # 文件后缀名
FILE_COUNT_SENTENCE = "FILE_COUNT_SENTENCE"
BOUNDARY = u"==========\n" #分隔符
intab = "\/:*?\"<>|"
outtab = "  ： ？“《》 "     #用于替换特殊字符
#trantab = maketrans(intab, outtab)

# 替换不能用作文件名的字符
def changechar(s):
    return s.translate(str.maketrans(intab,outtab))

# 处理sentence列表的方法函数
def getAddr(s):  #获取标注位置
    g = s.split(" | ")[0]
    return g
def getTime(s):  #获取添加时间
    g = s.split(" | ")[1]
    return g.split("\n\n")[0]
def getMark(s):  #获取标注内容
    g = s.split(" | ")[1]
    try:
        return g.split("\n\n")[1]
    except IndexError:
        #print("list index out of range due to empty content")
        return "empty content"

# 分割函数实现利用关键词进行简单的分割成列表
# 结果为每一条单独的笔记，包含书名，时间，位置和内容
f = open("My Clippings.txt", "r", encoding='utf-8')
content = f.read()  # 读取全部内容
content = content.replace(u'\ufeff', u'') #替换书名前的空格
clips = content.split(BOUNDARY)
print("列表个数：",clips.__len__()) # 获取列表的个数
#for i in range(0,4):  #打印出4条标注
    #print(clips[i])
    #print('---------')
sum = clips.__len__()

# 获取书名存储为列表books，获取除书名外的内容为sentence
both = []  #完整内容。格式为[['',''],['','']……]
books = [] #书名列表
sentence = []  #标注内容
for i in range(0,sum):
    book = clips[i].split("\n-")
    both.append(book)
    #print(book)
    if (book != ['']): # 如果书名非空
        books.append(changechar(book[0])) #添加书名，替换特殊字符，以便创建文件
        sentence.append(book[1])          #添加笔记
#print("both:",both)
#print("books:",books)
#print("sentence:",sentence)
print('笔记总数：',sentence.__len__())

# 去除书名列表中的重复元素
nameOfBooks = list(set(books))
nameOfBooks.sort(key=books.index)
print('书籍总数：',nameOfBooks.__len__())
#print(nameOfBooks)

# 根据不同书名建立网页文件
stceOfBookCnt = {}   # 记录每本书有几条标注的字典
#print(os.listdir())
if os.path.exists(TEMP_FOLDER):
    shutil.rmtree(TEMP_FOLDER)
    print('rm temp dir succ')
os.mkdir(TEMP_FOLDER) #创建一个books目录，用于存放书名网页文件
# print(os.listdir())
os.chdir(TEMP_FOLDER) #更改工作目录
curIndex = 0
for j in range(0,nameOfBooks.__len__()):
    # 网页文件的字符长度不能太长，以免无法在linux下创建
    if nameOfBooks[j].__len__() > 80:
        nameOfBooks[j] = nameOfBooks[j][0:80]  # 截取字符串

    f = open(nameOfBooks[j]+FILE_SUFFIX,'w',encoding='utf-8') # 创建网页文件
    f.write('# '+nameOfBooks[j]+'\n\n') #写入书名
    f.write('    '+'共' + FILE_COUNT_SENTENCE +'条评论'+'\n') #临时评论数目
    f.close()
    stceOfBookCnt.__setitem__(nameOfBooks[j],0)  # 清零每本书的标注数量

# 向文件添加标注内容
stce_succ_cnt = 0  # 向html文件添加笔记成功次数
stce_fail_cnt = 0  # 向html文件添加笔记失败次数
#print("html name:",os.listdir())
file_list = os.listdir(".") # 获取当前目录文件名，存放于file_list
for j in range(0,sentence.__len__()):
    temp = both[j]
    filename = changechar(temp[0][0:80])
    if (filename+FILE_SUFFIX in file_list ): # 检索字典
        s1 = getAddr(temp[1])  # 获取标注位置
        s2 = getTime(temp[1])  # 获取标注时间
        s3 = getMark(temp[1])  # 获取标注内容
        f = open(filename+FILE_SUFFIX,'a',encoding='utf-8') # 打开对应的文件
        if (s3 != '\n'):       # 如果文本内容非空
            stce_succ_cnt += 1
            cnt_temp = stceOfBookCnt[filename]
            stceOfBookCnt[filename] = cnt_temp+1
            f.write('\n### ' + str(cnt_temp+1) + '. ' + s3)
            f.write('\n    '+s2 + ' &&' + s1 +'\n')
            f.write('\n')
        else:
            stce_fail_cnt += 1
            print("empty txt",stce_fail_cnt,filename)
        f.close()
    else:
        print("can't find filename html :",temp[0]+".html")
print("sentence add succ cnt = ",stce_succ_cnt)
print("sentence add fail cnt = ",stce_fail_cnt)
#print(stceOfBookCnt)

# 添加总条数信息
for i in range(0,file_list.__len__()):
    f = open(file_list[i],'w+',encoding='utf-8') #打开对应的文件
    content = f.read()  # 读取全部内容
    print('content=', content)
    content.replace(FILE_COUNT_SENTENCE, str(111))
    f.write(content)
    f.close()

#向文件添加脚标
#print("html name:",os.listdir())
file_list = os.listdir(".") #获取当前目录文件名，存放于file_list
html_count = file_list.__len__()
print("file_list_count",html_count)
