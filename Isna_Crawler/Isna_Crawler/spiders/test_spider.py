import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from Isna_Crawler.items import CraigslistSampleItem

class MySpider(CrawlSpider):
    name = "test"
    allowed_domains = ["craigslist.org"]
    start_urls = ["http://sfbay.craigslist.org/search/npo"]

    def parse(self, response):
        titles = Selector(response).xpath("//span[@class='pl']")
        items = []
        for title in titles:
            item = CraigslistSampleItem()
            item["title"] = title.xpath("a/text()").extract()
            item["link"] = title.xpath("a/@href").extract()
            items.append(item)
        return items
