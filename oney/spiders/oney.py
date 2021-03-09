import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from oney.items import Article


class OneySpider(scrapy.Spider):
    name = 'oney'
    start_urls = ['https://blog.oney.fr/feedbacks?utf8=&search=&order=created_at.desc#none']

    def parse(self, response):
        links = response.xpath('//a[@class="permalink content_permalink"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next_page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/a/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('(//div[@class="body-bd"])[1]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
