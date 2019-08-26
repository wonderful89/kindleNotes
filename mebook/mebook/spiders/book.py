import scrapy
import re

### coding=utf-8

from urllib.parse import urlparse  # 3.7

# from urlparse import urlparse # 2.7

import sys

# reload(sys)
# sys.setdefaultencoding("utf8")

print("version = ", sys.version)

outFile = "data/books.markdown"
f = open(outFile, "a+", encoding="utf-8")
booksInfo = {}  # 全部书本信息，包括封面和描述


def checkAndCorrectUrl(str):
    if str.startswith("http"):
        return str
    matchObj = re.match(r".*http.*", str, re.M | re.I)
    if matchObj:
        name = matchObj.group(1)
        return "http{}".format(name)
    print("error data in checkAndCorrectUrl:{}".format(str))
    return ""


def getFileName(inputStr):
    matchObj = re.match(r".*《(.*)》.*", inputStr, re.M | re.I)
    if matchObj:
        name = matchObj.group(1)
        return name


def baiduSecret(inputStr):
    matchObj = re.match(r".*百度网盘密码：(.*) .*", inputStr, re.M | re.I)
    if matchObj:
        baidu = matchObj.group(1)
        baidu = str.strip(baidu)
        return baidu


def tianyiSecret(inputStr):
    matchObj = re.match(r".*天翼云盘密码：(.*)", inputStr, re.M | re.I)
    if matchObj:
        tianyi = matchObj.group(1)
        tianyi = str.strip(tianyi)
        # print("tianyi=", tianyi)
        return tianyi


class BookSpider(scrapy.Spider):
    name = "book"

    def start_requests(self):
        urls = ["http://www.shuwu.mobi/date/2019/08/page/1"]
        # urls = ["http://www.shuwu.mobi/30011.html"]
        # urls = ["http://www.shuwu.mobi/download.php?id=30013"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            # yield scrapy.Request(url=url, callback=self.parseDownloadPage)
            # yield scrapy.Request(url=url, callback=self.parseInfoPage)

    def parse(self, response):
        appsection = response.css("#primary .list")
        apps = appsection.css("li")
        for app in apps:
            url = app.css(".content h2 a::attr(href)").get()
            # p = urlparse(url)
            title = app.css(".content h2 a::attr(title)").get()
            title = getFileName(title)
            if title:
                booksInfo.__setitem__(title, {"infoUrl": url})
            yield scrapy.Request(url=url, callback=self.parseDownloadPage)
        # self.parseDownloadPage(response)
        # self.parseInfoPage(response)

    def parseDownloadPage(self, response):
        downUrl = response.css(".downlink strong a::attr(href)").get()
        print("downUrl = {}".format(downUrl))
        if downUrl:
            imgUrl = response.css(
                "#container-inner #primary #content p img::attr(src)"
            ).get()
            title = response.css("#container-inner #primary .sub::text").get()
            title = getFileName(title)
            descs = response.css("#link-report .intro span::text").get()
            dictInfo = booksInfo[title]
            dictInfo["imgUrl"] = imgUrl
            dictInfo["descs"] = descs
            booksInfo.__setitem__(title, dictInfo)
            # yield 应该是直接返回调用流
            yield scrapy.Request(url=downUrl, callback=self.parseInfoPage)

    def parseInfoPage(self, response):
        downUrlInfo = response.css("body .list a")
        if downUrlInfo:
            outInfo = {"channels": []}
            markDownStr = ""
            # curIndex = 0
            for index, downInfo in enumerate(downUrlInfo):
                # print("downInfo:", downInfo)
                curIndex = index + 1
                print("curIndex = ", curIndex)
                realDownloadUrl = downInfo.css("a::attr(href)").get()
                text = downInfo.css("a::text").get()
                text2 = downInfo.css("a font::text").get()
                if not text:
                    text = text2

                despInfo = response.css("body .desc p")
                obj3 = despInfo[3]
                dataStr = obj3.css("p::text").get()
                obj5 = despInfo[5]
                secretStr = obj5.css("p::text").get()
                obj0 = despInfo[0]
                name = obj0.css("p::text").get()
                name = getFileName(name)
                print("处理文件=", name)
                if re.match(r".*百度.*", text, re.M | re.I):
                    secretStr = baiduSecret(secretStr)
                elif re.match(r".*天翼.*", text, re.M | re.I):
                    secretStr = tianyiSecret(secretStr)
                else:
                    secretStr = ""
                outInfo["name"] = name
                outInfo["time"] = dataStr
                outInfo["channels"].append(
                    {
                        "channel": text,
                        "url": checkAndCorrectUrl(realDownloadUrl),
                        "secret": secretStr,
                    }
                )
            # yield (outInfo)
            markDownStr += "### {}. {}: {}\n".format(
                curIndex, outInfo["name"], outInfo["time"]
            )
            bookInfo = booksInfo[name]
            if bookInfo:
                imgUrl = bookInfo["imgUrl"]
                descs = bookInfo["descs"]
                infoUrl = bookInfo["infoUrl"]
                # markDownStr += "![]({})\n".format(img)
                markDownStr += '<img src="{}" width="120" align=center />\n'.format(
                    imgUrl
                )
                markDownStr += "```\n{}\n```\n".format(descs)
                markDownStr += "[点击查看介绍界面]({})\n".format(infoUrl)
            for cc in outInfo["channels"]:
                markDownStr += "{}: [点击下载]({}) : {}\n".format(
                    cc["channel"], cc["url"], cc["secret"]
                )
            markDownStr += "\n"
            f.write(markDownStr)
            yield outInfo


# f.close()
