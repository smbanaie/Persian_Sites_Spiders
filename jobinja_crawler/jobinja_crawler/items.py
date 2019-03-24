# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobinjaCompanyItem(scrapy.Item):
    title_fa = scrapy.Field()  # عنوان فارسی شرکت
    title_en = scrapy.Field()  # عنوان لاتین شرکت
    open_jobs = scrapy.Field()  # تعداد شغل‌های باز و موردنیاز
    category = scrapy.Field()  # گروه شغلی
    company_size = scrapy.Field()  # اندازه شرکت
    company_site = scrapy.Field()  # سایت شرکت
    year = scrapy.Field()  # سال تاسیس


class JobinjaJobItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()  # عنوان آگهی
    company_fa = scrapy.Field()  # نام شرکت به فارسی
    category = scrapy.Field()  # گروه
    location = scrapy.Field()  # مکان
    minExperience = scrapy.Field()  # حداقل سابقه کار مورد نیاز
    jobType = scrapy.Field()  # نوع شغلی
    salary = scrapy.Field()  # حقوق
    desc = scrapy.Field()  # توضیح
    company_desc = scrapy.Field()  # توضیح شرکت
    skills = scrapy.Field()  # مهارت های مورد نیاز
    period = scrapy.Field()  # بازه زمانی اشتغال
    militaryServiceStatus = scrapy.Field()  # وضعیت نظام وظیفه
    gender = scrapy.Field()  # جنسیت
    degree = scrapy.Field()  # حداقل مدرک مورد نیاز
    language = scrapy.Field()  # زبان‌های مورد نیاز
    allowedMajors = scrapy.Field()  # مدارک تحصیلی مورد نیاز
    active = scrapy.Field()  # فعال یا غیر فعال بودن آگهی