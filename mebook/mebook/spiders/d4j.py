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


def getDownloadUrl(str):
    list = re.split("/", str)
    list2 = re.split("\.", list[3])
    retId = list2[0]
    newUrl = "https://www.d4j.cn/download.php?id={}".format(retId)
    print(newUrl)
    return newUrl


# 在介绍页去下载地址
def getDownloadUrl2(str):
    list = re.split("=", str)
    retId = list[1]
    newUrl = "https://www.d4j.cn/{}.html".format(retId)
    print(newUrl)
    return newUrl


class D4jBookSpider(scrapy.Spider):
    name = "d4j"

    def start_requests(self):
        urls = []
        for ii in range(1, 33):
            print("ii = {}".format(ii))
            urls.append(
                "https://www.d4j.cn/category/book/lishirenwu/page/{}".format(ii)
            )
        urls = ["https://www.d4j.cn/"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        appsection = response.css(".col-md-8")
        apps = appsection.css(".kratos-entry-border-new")
        for app in apps:
            url = app.css(".kratos-entry-title-new a::attr(href)").get()
            title = app.css(".kratos-entry-title-new a::text").get()
            str = "url = {}, title = {}".format(url, title)
            # print(str)
            yield scrapy.Request(
                url=getDownloadUrl(url), callback=self.parseDownloadPage
            )

    def parseDownloadPage(self, response):
        title = response.css(".content h2::text").get()
        url = response.css(".downfile a::attr(href)").get()
        secrets = response.css(".plus_l ul li")
        baiduSecret = secrets[3].css("font::text").get()
        str = "url = {}, secret = {}, title = {}".format(url, baiduSecret, title)
        print(str)
        if url == None:
            originUrl = response.url
            print("重新尝试：originUrl = {}".format(originUrl))
            newUrl = getDownloadUrl2(originUrl)
            yield scrapy.Request(
                newUrl, callback=self.parseDownloadPage2, dont_filter=True
            )
        else:
            yield (
                {
                    "name": title,
                    "channels": [
                        {
                            "channel": "百度网盘",
                            "name": title,
                            "url": url,
                            "secret": baiduSecret,
                        }
                    ],
                }
            )

    def parseDownloadPage2(self, response):
        print("in parseDownloadPage2 , url={}".format(response.url))
        title = response.css(".kratos-entry-title::text").get()
        url = response.css(".downcloud::attr(href)").get()
        baiduSecret = response.xpath(
            '//*[@id="main"]/article/div[1]/div[1]/p[3]/text()'
        ).get()

        children = response.css(".kratos-post-content > p")
        if children == None:
            print("children === None")
        else:
            # print("children = {}".format(children))
            lastP = children[len(children) - 1]
            baiduSecret = lastP.xpath("text()").get()

        if baiduSecret == None:
            print("尝试直接获取1")
            baiduSecret = lastP.xpath(
                '//*[@id="main"]/article/div[1]/div[1]/div[4]/text()'
            ).get()

        if baiduSecret == None:
            print("尝试直接获取2")
            children = response.css("#link-report .intro > p")
            lastP = children[len(children) - 2]
            baiduSecret = lastP.xpath("text()").get()

        if baiduSecret == None:
            print("baiduSecret = {}".format(baiduSecret))
        else:
            baiduSecret = baiduSecret[-4:]

        str = "tryAgain url = {}, secret = {}, title = {}".format(
            url, baiduSecret, title
        )
        print(str)
        if url == None or baiduSecret == None:
            print("重新尝试失败：response = {}".format(response))
        else:
            yield (
                {
                    "name": title,
                    "channels": [
                        {
                            "channel": "百度网盘",
                            "name": title,
                            "url": url,
                            "secret": baiduSecret,
                        }
                    ],
                }
            )
