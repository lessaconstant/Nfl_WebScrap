import scrapy


class TeamsDataSpider(scrapy.Spider):
    name = "teams_data"
    allowed_domains = ["footballdb.com"]
    start_urls = ["https://footballdb.com"]

    def parse(self, response):
        pass
