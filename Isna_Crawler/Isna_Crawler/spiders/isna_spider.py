# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from Isna_Crawler.items import IsnaCrawlerItem
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor

class IsnaSpider(CrawlSpider):
    name = "isna"
    allowed_domains = ["www.isna.ir"]
    start_urls = [
        "http://www.isna.ir/",
        # "http://www.isna.ir/page/archive.xhtml?date=1395%2F03%2F01&page=1&lang=fa&pageSize=20&cerveesCode=all",
        # "http://www.isna.ir/search?lang=fa&q=%D8%AC%D8%B4%D9%86%D9%88%D8%A7%D8%B1%D9%87",
    ]
    rules = [Rule(LinkExtractor(allow=('/fa/news/\d+/', )), callback='parse_item', follow=True)]

    def parse_item(self, response):
        item = IsnaCrawlerItem()
        selector  = response.selector
        item['title'] = selector.xpath('//div[@class="titr"]//p/text()').extract()[0].strip()
        item['body'] = ' '.join([x.strip() for x in (selector.xpath('//div[@class="body"]//text()').extract())])
        item['body'] = item['body'].replace('\"','').replace("\'",'').replace(u"«","").replace(u"»","").replace(",","").replace(u"انتهای پیام","")
        item['category'] = selector.xpath('//div[@class="cervees"]/text()').extract()[0].replace(u"سرویس:","").replace(u"«","").replace(u"»","").replace(u'\"',"").strip()
        item['pubDate'] = selector.xpath('//div[@class="newsPubDate"]/text()').extract()[0].strip()
        item["tags"] = []
        tags = selector.xpath('//div[@class="tag"]/a')
        if tags :
            for tag in tags :
                item["tags"].append(tag.xpath("text()").extract()[0])

        yield item
