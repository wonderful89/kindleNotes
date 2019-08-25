import scrapy
import re
from urllib.parse import urlparse


class ExampleScrapy(scrapy.Spider):
    name = "example"

    def start_requests(self):
        urls = ["http://www.shuwu.mobi/date/2019/08"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        appsection = response.css("#primary .list")
        apps = appsection.css("li")
        for app in apps:
            url = app.css(".content h2 a::attr(href)").get()
            yield scrapy.Request(url=url, callback=self.parseDownUrl)
        # self.parseDownUrl(response)

    def parseDownUrl(self, response):
        print("in parseDownUrl")
        downUrl = response.css(".downlink strong a::attr(href)").get()
        print("downUrl = {}".format(downUrl))
        if downUrl:
            yield scrapy.Request(url=downUrl, callback=self.parse)
            # scrapy.Request(url=downUrl, callback=self.parse)
