# -*- coding: utf-8 -*-
import scrapy
import json

from scrapy_splash import SplashRequest
from scrapy.loader import ItemLoader
from scrapy.http.headers import Headers

from newco.items import BerrybenkaItem


RENDER_HTML_URL = "http://splash:8050/render.html"

class BerrybenkaSpider(scrapy.Spider):
    name = "berrybenka"
    allowed_domains = ["berrybenka.com"]

    MAIN_URL = 'http://berrybenka.com/'

    start_urls = ['http://berrybenka.com/clothing/tops/women/']

    headers = Headers({'Content-Type': 'application/json'})
    body = {"wait": 0.5}

    page_index = 0

    items_per_page = 48

    def start_requests(self):
        for url in self.start_urls:
            self.body['url'] = url
            yield scrapy.Request(
                RENDER_HTML_URL, callback=self.parse,
                method="POST", body=json.dumps(self.body, sort_keys=True),
                headers=self.headers)


    def parse(self, response):
        """
        Vertical crawl
        """
        
        detail_links = response.xpath('//a[@class="catalog-img"]/@href').extract()

        for link in detail_links:
            yield scrapy.Request(url=link, callback=self.parse_item)

        """
        Horizontal crawl
        Mulai dari /0
        Cek apakh ada link 'Next'
        Kalo tidak ada maka berhenti
        kalo ada maka tambahkan 48 jadi /sebelumnya+48 untuk url baru yg di scrape
        """
        next_page = response.xpath('//li[@class="next right"]')
        self.page_index += 1

        for url in self.start_urls:
            self.body['url'] = url+str(self.page_index * self.items_per_page)

            print self.body['url']

            yield scrapy.Request(
                RENDER_HTML_URL, callback=self.parse,
                method="POST", body=json.dumps(self.body, sort_keys=True),
                headers=self.headers, dont_filter=True)


    def parse_item(self, response):
        item = BerrybenkaItem()
        item['name'] = response.xpath('//div[@class="prod-spec-title"]/h1/text()').extract()
        item['brand'] = response.xpath('//div[@class="prod-spec-title"]/h2/a/text()').extract()
        item['description'] = response.xpath('//p[@id="product_description"]/text()').extract()
        item['price'] = response.xpath('//div[@class="prod-spec-title"]/p/text()').extract()
        item['url'] = response.url

        images = [response.xpath('//div[@class="detail-photo left"]/div[@class="big-photo left"]/a/img/@src').extract()]

        item['image_urls'] = images + response.xpath('//div[@class="detail-photo left"]/div[@class="small-photo left"]/ul/li/a/img/@src').extract()

        return item
