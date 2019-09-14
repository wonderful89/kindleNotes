import scrapy
import re
from urllib.parse import urlparse


class ExampleScrapy(scrapy.Spider):
    name = "example"

    def start_requests(self):
        urls = ["https://www.d4j.cn/4604.html"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parseDownloadPage2)

    def parseDownloadPage2(self, response):
        print("in parseDownloadPage2 , url={}".format(response.url))
        title = response.css(".kratos-entry-title::text").get()
        url = response.css(".downcloud::attr(href)").get()
        baiduSecret = response.xpath(
            '//*[@id="main"]/article/div[1]/div[1]/p[3]/text()'
        ).get()

        # children = response.css(".kratos-post-content > p")
        lastP = response.css("text()").getall()
        print("lastP = {}".format(lastP))
        if lastP == None:
            print("lastP === None")
        else:
            # print("children = {}".format(children))
            # lastP = children[len(children) - 1]
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
