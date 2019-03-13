# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobinjaCompanyItem(scrapy.Item):
    title_fa = scrapy.Field()
    title_en = scrapy.Field()
    open_jobs= scrapy.Field()
    category = scrapy.Field()
    company_size = scrapy.Field()
    company_site = scrapy.Field()
    year = scrapy.Field()

class JobinjaJobItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    company_fa = scrapy.Field()
    category = scrapy.Field()
    location = scrapy.Field()
    minExperience = scrapy.Field()
    jobType = scrapy.Field()
    salary = scrapy.Field()
    desc = scrapy.Field()
    company_desc = scrapy.Field()
    skills = scrapy.Field()
    period = scrapy.Field()
    militaryServiceStatus = scrapy.Field()
    gender = scrapy.Field()
    degree = scrapy.Field()
    language = scrapy.Field()
    allowedMajors = scrapy.Field()
    active = scrapy.Field()
