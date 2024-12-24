import scrapy
import logging
import re
from scrapper.items import EngravingItem

class OpticalSpider(scrapy.Spider):
    name = "opticalspider"
    allowed_domains = ["www.france-optique.com"]

    start_urls = [
        "https://www.france-optique.com/gravures/fournisseur=2399",
        "https://www.france-optique.com/gravures/fournisseur=1344",
        "https://www.france-optique.com/gravures/fournisseur=70",
        "https://www.france-optique.com/gravures/fournisseur=521",
        "https://www.france-optique.com/gravures/fournisseur=1488",
        "https://www.france-optique.com/gravures/fournisseur=130",
        "https://www.france-optique.com/gravures/fournisseur=1958",
        "https://www.france-optique.com/gravures/fournisseur=2217",
        "https://www.france-optique.com/gravures/fournisseur=2532",
        "https://www.france-optique.com/gravures/fournisseur=644",
        "https://www.france-optique.com/gravures/fournisseur=1838",
        "https://www.france-optique.com/gravures/fournisseur=561",
        "https://www.france-optique.com/gravures/fournisseur=711",
        "https://www.france-optique.com/gravures/fournisseur=2395",
        "https://www.france-optique.com/gravures/fournisseur=127",
        "https://www.france-optique.com/gravures/fournisseur=659",
        "https://www.france-optique.com/gravures/fournisseur=789",
        "https://www.france-optique.com/gravures/fournisseur=2069",
        "https://www.france-optique.com/gravures/fournisseur=1407",
        "https://www.france-optique.com/gravures/fournisseur=2397",
        "https://www.france-optique.com/gravures/fournisseur=2644",
        "https://www.france-optique.com/gravures/fournisseur=2414",
    ]

    def parse(self, response):
        self.log(f"Parsing page: {response.url}", level=logging.INFO)

        category_elements = response.xpath('//div[@class="row tr group"]')
        for category in category_elements:
            category_name = category.xpath('./text()').get()
            if category_name:
                category_name = category_name.strip()

            engraving_rows = category.xpath('./following-sibling::div[@class="row tr"]')
            for engraving_row in engraving_rows:
                
                item = EngravingItem()

                item['category'] = category_name
                item['glass_name'] = engraving_row.xpath(
                    './/div[contains(@class, "col s4 m4")]/p/text()'
                ).get()
                item['nasal_engraving'] = engraving_row.xpath(
                    './/div[contains(@class, "col s1 m1")][2]/img/@src'
                ).get() or engraving_row.xpath(
                    './/div[contains(@class, "col s1 m1")][2]/p[@class="gravure_txt"]/b/text()'
                ).get()
                item['glass_index'] = engraving_row.xpath(
                    './/div[contains(@class, "col s1 m1")][4]/p/text()'
                ).get()
                item['material'] = engraving_row.xpath(
                    './/div[contains(@class, "col s1 m1")][5]/p/text()'
                ).get()

                match = re.search(r'fournisseur=(\d+)', response.url)
                if match:
                    item['glass_supplier_id'] = match.group(1)

                self.log(f"Extracted item: {item}", level=logging.DEBUG)
                yield item
