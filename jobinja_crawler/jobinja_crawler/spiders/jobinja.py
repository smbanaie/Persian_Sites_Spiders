# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from jobinja_crawler.items import JobinjaCompanyItem, JobinjaJobItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
import codecs,os
from datetime import datetime
import logging


class JobinjaSpider(CrawlSpider):
    name = "jobinja"
    allowed_domains = ["www.jobinja.ir", "jobinja.ir"]
    start_urls = [
        "https://jobinja.ir/companies"
    ]

    #
    def __init__(self):
        super().__init__()
        if not os.path.exists(self.company_details+datetime.now().strftime("-%Y-%m")+'.csv'):
            self.write_company_info({}, header=True)
            self.write_job_info({}, header=True)

    rules = [Rule(LinkExtractor(allow=r'/companies/[^/]+$', ), callback='parse_company', follow=False),
             Rule(LinkExtractor(allow=r'/companies/[a-zA-Z0-9\-_]+/jobs$', ), callback='parse_company_jobs',
                  follow=True),
             Rule(LinkExtractor(allow=r'/companies/[a-zA-Z0-9\-_]+/jobs/\.*', ), callback='parse_jobs', follow=False),
             Rule(LinkExtractor(allow=[r'\/companies\?page=\d+', r'\/companies$'], ), follow=True)
             ]
    # logger = logging.getLogger(__name__)

    company_details = r"companies_info"
    company_jobs_details = r"companies_jobs"

    def parse_company(self, response):
        yield Request(response.request.url + "/jobs",
                      meta={
                          'dont_redirect': True,
                          'handle_httpstatus_list': [302]
                      }, callback=self.parse_company_jobs)

    def parse_company_jobs(self, response):
        item = JobinjaCompanyItem()
        tiltle = response.xpath('//h2[@class="c-companyHeader__name"]/text()').extract()
        item["title_fa"] = tiltle[0]
        item["title_en"] = tiltle[1]
        item["open_jobs"] = response.css('.c-companyHeader__navigatorOpenJobs::text').extract_first()
        company_metadata = [x.strip() for x in
                            response.xpath('//div[@class="c-companyHeader__meta"]/span//text()').extract() if
                            x.strip() != ""]

        if len(company_metadata) == 4:
            item["year"] = company_metadata[0].strip()
            item["category"] = company_metadata[1].strip()
            item["company_size"] = company_metadata[2].strip()
            item["company_site"] = company_metadata[3].strip()
        elif len(company_metadata) == 3:
            item["category"] = company_metadata[0].strip()
            item["company_size"] = company_metadata[1].strip()
            item["company_site"] = company_metadata[2].strip()
            item["year"] = str(None)
        else:
            item["category"] = company_metadata[0].strip()
            item["company_size"] = company_metadata[1].strip()
            item["year"] = str(None)
            item["company_site"] = str(None)
        self.write_company_info(item)
        yield item

    def parse_jobs(self, response):
        item = JobinjaJobItem()
        item["company_fa"] = response.css('h2.c-companyHeader__name::text').get().strip()
        item["name"] = response.css('.c-jobView__titleText::text').get().strip()

        item["active"] = True
        submit_cv = response.xpath("//input[@value='ارسال رزومه']").get()
        if submit_cv == None:
            item["active"] = False

        categories = response.css(".c-jobView__firstInfoBox") \
            .xpath(".//li[h4/text()='دسته‌بندی شغلی']//span/text()").getall()
        item["category"] = ""
        if categories:
            item["category"] = "^".join([cat.strip() for cat in categories if cat != ""])
        location = response.css(".c-jobView__firstInfoBox") \
            .xpath(".//li[h4/text()='موقعیت مکانی']//span/text()").getall()
        item["location"] = ""
        if location:
            item["location"] = "^".join(
                [" ".join([word.strip() for word in loc.split() if word != ""]) for loc in location if loc != ""])
        jobType = response.css(".c-jobView__firstInfoBox") \
            .xpath(".//li[h4/text()='نوع همکاری']//span/text()").getall()
        item["jobType"] = ""
        if jobType:
            item["jobType"] = "^".join([jt.strip() for jt in jobType if jt != ""])
        minExperience = response.css(".c-jobView__firstInfoBox") \
            .xpath(".//li[h4/text()='حداقل سابقه کار']//span/text()").getall()
        item["minExperience"] = ""
        if minExperience:
            item["minExperience"] = "^".join([me.strip() for me in minExperience if me != ""])

        salary = response.css(".c-jobView__firstInfoBox") \
            .xpath(".//li[h4/text()='حقوق']//span/text()").getall()
        item["salary"] = ""
        if salary:
            item["salary"] = "^".join(
                [" ".join([word.strip() for word in me.split() if word != ""]) for me in salary if me != ""])

        period = response.css(".c-jobView__firstInfoBox") \
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

        allowedMajors = response.xpath(
            "//ul[@class='c-infoBox']/li[h4/text()='رشته‌های تحصیلی مرتبط']/div/span/text()").getall()
        item["allowedMajors"] = ""
        if allowedMajors:
            item["allowedMajors"] = "^".join(
                [" ".join([word.strip() for word in ajob.split() if word != ""]) for ajob in allowedMajors if
                 ajob != ""])

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

        self.write_job_info(item)
        yield item

    def write_company_info(self, item, header=False):
        f = codecs.open(self.company_details+datetime.now().strftime("-%Y-%m")+'.csv', "a", encoding="utf8")
        if not header:
            row_csv = "{0},{1},{2},{3},{4},{5},{6}\r\n".format(item["title_fa"].replace(",", "،"),
                                                               item["title_en"].replace(",", "،"),
                                                               item["open_jobs"].replace(",", "،"),
                                                               item["category"].replace(",", "،"),
                                                               item["company_size"].replace(",", "،"),
                                                               item["company_site"].replace(",", "،"),
                                                               item["year"].replace(",", "،"))
        else:
            row_csv = "{0},{1},{2},{3},{4},{5},{6}\r\n".format("title_fa", "title_en", "open_jobs",
                                                               "category", "company_size", "company_site",
                                                               "year")
        f.write(row_csv)
        f.close()

    def write_job_info(self, item, header=False):
        f = codecs.open(self.company_jobs_details+datetime.now().strftime("-%Y-%m")+'.csv', "a", encoding="utf8")
        if not header:
            row_csv = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}," \
                      "{13},{14},{15}\r\n" \
                .format(item["company_fa"].replace(",", "،"), item["name"].replace(",", "،"),
                        item["category"].replace(",", "،"), item["location"].replace(",", "،"),
                        item["jobType"].replace(",", "،"), item["minExperience"].replace(",", "،"),
                        item["salary"].replace(",", "،"), item["skills"].replace(",", "،"),
                        item["gender"].replace(",", "،"), item["allowedMajors"].replace(",", "،"),
                        item["active"], item["period"].replace(",", "،"),
                        item["degree"].replace(",", "،"), item["language"].replace(",", "،"),
                        item["desc"].replace(",", "،"), item["company_desc"].replace(",", "،"))
        else:
            row_csv = "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}," \
                      "{13},{14},{15}\r\n" \
                .format("company_fa", "name", "category",
                        "location", "jobType", "minExperience",
                        "salary", "skills", "gender", "allowedMajors",
                        "active", "period", "degree", "language",
                        "desc", "company_desc")

        f.write(row_csv)
        f.close()
