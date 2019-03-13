# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from jobinja_crawler.items import JobinjaCompanyItem,JobinjaJobItem
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
import codecs
import logging

class JobInja(CrawlSpider):
    name = "jobinja"
    allowed_domains = ["www.jobinja.ir","jobinja.ir"]
    start_urls = [
    "https://jobinja.ir/companies"
    ]
    #
    rules = [Rule(LinkExtractor(allow=r'/companies/[^/]+$', ), callback='parse_company', follow=False),
             Rule(LinkExtractor(allow=r'/companies/[a-zA-Z0-9\-_]+/jobs$', ), callback='parse_company_jobs', follow=True),
             Rule(LinkExtractor(allow=r'/companies/[a-zA-Z0-9\-_]+/jobs/\.*', ), callback='parse_jobs', follow=False),
             Rule(LinkExtractor(allow=[r'\/companies\?page=\d+', r'\/companies$'], ), follow=True)
             ]
    # logger = logging.getLogger(__name__)

    company_details  = r"companies_info.csv"
    company_jobs_details = r"companies_jobs.csv"

    def parse_company(self, response):
        yield Request(response.request.url +"/jobs",
                      meta = {
                          'dont_redirect': True,
                          'handle_httpstatus_list': [302]
              }, callback=self.parse_company_jobs)

    def parse_company_jobs(self, response):
        item = JobinjaCompanyItem()
        tiltle = response.xpath('//h2[@class="c-companyHeader__name"]/text()').extract()
        item["title_fa"] = tiltle[0]
        item["title_en"] = tiltle[1]
        item["open_jobs"] = response.css('.c-companyHeader__navigatorOpenJobs::text').  extract_first()
        company_metadata = [x.strip() for x in
                    response.xpath('//div[@class="c-companyHeader__meta"]/span//text()').extract() if x.strip() != ""]

        if len(company_metadata) == 4:
            item["year"] = company_metadata[0].strip()
            item["category"]  = company_metadata[1].strip()
            item["company_size"]  = company_metadata[2].strip()
            item["company_site"]  = company_metadata[3].strip()
        elif len(company_metadata) == 3:
            item["category"] = company_metadata[0].strip()
            item["company_size"] = company_metadata[1].strip()
            item["company_site"] = company_metadata[2].strip()
            item["year"] = str(None)
        else :
            item["category"] = company_metadata[0].strip()
            item["company_size"] = company_metadata[1].strip()
            item["year"] = str(None)
            item["company_site"] = str(None)
        f = codecs.open(self.company_details, "a", encoding="utf-8")
        row_csv = "{0},{1},{2},{3},{4},{5},{6}\r\n".format(item["title_fa"], item["title_en"], item["open_jobs"],
                                                           item["category"], item["company_size"], item["company_site"],
                                                           item["year"])
        f.write(row_csv)
        f.close()
        yield item

    def parse_jobs(self, response):
        item = JobinjaJobItem()
        item["company_fa"] = response.css('h2.c-companyHeader__name::text').get().strip()
        item["name"] = response.css('.c-jobView__titleText::text').get().strip()

        item["active"] = True
        submit_cv = response.xpath("//input[@value='ارسال رزومه']").get()
        if submit_cv == None :
            item["active"] = False

        categories = response.css(".c-jobView__firstInfoBox")\
            .xpath(".//li[h4/text()='دسته‌بندی شغلی']//span/text()").getall()
        item["category"] =""
        if categories:
            item["category"] = "^".join([cat.strip() for cat in categories if cat != ""])
        location = response.css(".c-jobView__firstInfoBox")\
            .xpath(".//li[h4/text()='موقعیت مکانی']//span/text()").getall()
        item["location"] = ""
        if location:
            item["location"] =  "^".join([ " ".join([word.strip() for word in  loc.split() if word!=""]) for loc in location if loc != ""])
        jobType = response.css(".c-jobView__firstInfoBox")\
            .xpath(".//li[h4/text()='نوع همکاری']//span/text()").getall()
        item["jobType"]=""
        if jobType:
            item["jobType"] = "^".join([jt.strip() for jt in jobType if jt != ""])
        minExperience = response.css(".c-jobView__firstInfoBox")\
            .xpath(".//li[h4/text()='حداقل سابقه کار']//span/text()").getall()
        item["minExperience"]=""
        if minExperience:
            item["minExperience"] = "^".join([me.strip() for me in minExperience if me != ""])

        salary = response.css(".c-jobView__firstInfoBox") \
            .xpath(".//li[h4/text()='حقوق']//span/text()").getall()
        item["salary"] = ""
        if salary:
            item["salary"] = "^".join([ " ".join([word.strip() for word in  me.split() if word!=""]) for me in salary if me != ""])

        period = response.css(".c-jobView__firstInfoBox")\
            .xpath(".//li[h4/text()='تاریخ شروع و پایان همکاری']//span/text()").getall()
        item["period"] = ""
        if period:
            item["period"] = "^".join(
                [" ".join([word.strip() for word in pr.split() if word != ""]) for pr in period if pr != ""])

        skills = response.xpath("//ul[@class='c-infoBox']/li[h4/text()='مهارت‌های مورد نیاز']/div/span/text()").getall()
        item["skills"] = ""
        if skills:
            item["skills"] = "^".join(
                [" ".join([word.strip() for word in sk.split() if word != ""]) for sk in skills if sk != ""])

        gender = response.xpath("//ul[@class='c-infoBox']/li[h4/text()='جنسیت']/div/span/text()").getall()
        item["gender"] = ""
        if gender:
            item["gender"] = "^".join(
                [" ".join([word.strip() for word in gn.split() if word != ""]) for gn in gender if gn != ""])

        allowedMajors = response.xpath("//ul[@class='c-infoBox']/li[h4/text()='رشته‌های تحصیلی مرتبط']/div/span/text()").getall()
        item["allowedMajors"] = ""
        if allowedMajors:
            item["allowedMajors"] = "^".join(
                [" ".join([word.strip() for word in ajob.split() if word != ""]) for ajob in allowedMajors if ajob != ""])

        degree = response.xpath(
            "//ul[@class='c-infoBox']/li[h4/text()='حداقل مدرک تحصیلی']/div/span/text()").getall()
        item["degree"] = ""
        if degree:
            item["degree"] = "^".join(
                [" ".join([word.strip() for word in deg.split() if word != ""]) for deg in degree if deg != ""])

        language = response.xpath(
            "//ul[@class='c-infoBox']/li[h4/text()='زبان‌های مورد نیاز']/div/span/text()").getall()
        item["language"] = ""
        if language:
            item["language"] = "^".join(
                [" ".join([word.strip() for word in lang.split() if word != ""]) for lang in language if lang != ""])

        desc = response.css("div.s-jobDesc > p::text").getall()
        item["desc"] = ""
        if desc:
            item["desc"] = " ".join([dc.strip().replace(",", "،") for dc in desc if dc.strip() != ""])

        company_desc = response.xpath("//div[@class='o-box__text']//text()").getall()
        item["company_desc"] = ""
        if company_desc:
            item["company_desc"] = " ".join(
                [cd.strip().replace(",", "،") for cd in company_desc if cd.strip() != ""])

        militaryServiceStatus = response.xpath(
            "//ul[@class='c-infoBox']/li[h4/text()='وضعیت نظام وظیفه']/div/span/text()").getall()
        item["militaryServiceStatus"] = ""
        if militaryServiceStatus:
            item["militaryServiceStatus"] = "^".join(
                [" ".join([word.strip() for word in ms.split() if word != ""])
                 for ms in militaryServiceStatus if ms != ""])

        f = codecs.open(self.company_jobs_details, "a", encoding="utf-8")
        row_csv = "Company :{0},title:{1},categories: {2},location: {3}, jobType: {4},minExperience:{5},salary: {6}," \
                  "skills:{7}, gender: {8}, allowedMajors:{9},active: {10},period: {11}, degree: {12}," \
                  "language: {13},desc: {14}, company_desc: {15},link:{16}\r\n"\
            .format(item["company_fa"], item["name"], item["category"],
                    item["location"], item["jobType"], item["minExperience"],
                    item["salary"], item["skills"], item["gender"], item["allowedMajors"],
                    item["active"], item["period"], item["degree"], item["language"],
                    item["desc"], item["company_desc"], response.request.url)
        f.write(row_csv)
        f.close()
