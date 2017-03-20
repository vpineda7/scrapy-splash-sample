# -*- coding: utf-8 -*-
import scrapy
import urlparse
import json

from scrapy_splash import SplashRequest
from scrapy.loader import ItemLoader
from scrapy.http.headers import Headers

from zalora.items import ZaloraItem

RENDER_HTML_URL = "http://splash:8050/render.html"


class BasicSpider(scrapy.Spider):
    name = "zalora"
    allowed_domains = ["zalora.co.id"]
    MAIN_URL = 'https://www.zalora.co.id/'

    start_urls = ['https://www.zalora.co.id/women/pakaian/atasan/?from=header']

    headers = Headers({'Content-Type': 'application/json'})
    body = {"wait": 0.5}

    def start_requests(self):
        for url in self.start_urls:
            self.body['url'] = url
            yield scrapy.Request(RENDER_HTML_URL, callback=self.parse, method="POST",
                body=json.dumps(self.body, sort_keys=True), headers=self.headers)

    def parse(self, response):

        item_selector = response.xpath('//a[@class="b-catalogList__itmLink itm-link"]/@href')
        idx = 0
        for url in item_selector.extract():
            item_detail_url = self.MAIN_URL+url
            yield scrapy.Request(url=item_detail_url, callback=self.parse_item)
            #self.body['url'] = item_detail_url
            #yield scrapy.Request(RENDER_HTML_URL, callback=self.parse_item, method="POST",
                #body=json.dumps(self.body, sort_keys=True), headers=self.headers)

        next_selector = response.xpath('//a[@title="Berikutnya"]//@href')

        prev_url = ''
        for url in next_selector.extract():
            next_url = self.MAIN_URL + url

            if prev_url == next_url:
                continue

            print next_url
            prev_url = next_url

            self.body["url"] = next_url
            yield scrapy.Request(url=RENDER_HTML_URL,
                callback=self.parse, method="POST",
                body=json.dumps(self.body),
                headers=self.headers, dont_filter=True)

    def parse_item(self, response):
        item = ZaloraItem()
        item['name'] = response.xpath('//div[@class="js-prd-brand product__brand"]/a/text()').extract()
        item['description'] = response.xpath('//div[@class="product__title fsm"]/text()').extract()
        item['url'] = response.url

        price = response.xpath('//div[@class="price-box__special-price"]/span/span[@class="js-detail_updateSku_lowestPrice"]/span[@class="value"]/text()').extract()

        if len(price) == 0:
            price = response.xpath('//div[@class="price-box lfloat"]/div/span/text()').extract()

        item['price'] = price

        image_urls = response.xpath('//ul[@class="prd-moreImagesList ui-listItemBorder ui-listLight swiper-wrapper"]/li/a/img/@src').extract()
        #item['image_urls'] = image_urls
        item['image_urls'] = self.parse_images_urls(image_urls)

        return item

    def parse_images_urls(self, images_urls):
        parsed_images_urls = list()
        HTTP_APPENDIX = 'http://'
        real_image_index = 1

        for url in images_urls:
            parsed_images_urls.append(HTTP_APPENDIX + url.split(HTTP_APPENDIX)[real_image_index])

        return parsed_images_urls
