import scrapy
import re
import logging
from scrapers.items import ScrapersItem
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider


class Glass_spiderSpider(scrapy.Spider):
    name = "glass_spider"
    allowed_domains = ["www.france-optique.com"]

    # Ajout des URLs de tous les fournisseurs
    start_urls = [
        "https://www.france-optique.com/gravures/fournisseur=2399"
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

        # Extraction des catégories
        category_elements = response.xpath('//div[@class="row tr group"]')
        if not category_elements:
            self.log("No categories found on the page", level=logging.WARNING)
            return

        for category in category_elements:
            category_name = category.xpath('./text()').get()
            if category_name:
                category_name = category_name.strip()
            else:
                self.log(f"Category name is missing on page: {response.url}", level=logging.WARNING)
                continue

            # Extraction des lignes de gravure dans cette catégorie
            engraving_rows = category.xpath('./following-sibling::div[@class="row tr"]')
            if not engraving_rows:
                self.log(f"No engravings found for category: {category_name}", level=logging.WARNING)
                continue

            for engraving_row in engraving_rows:
                item = ScrapersItem()
                item['category'] = category_name

                # Extraction des détails de gravure
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

                # Extraction de l'ID du fournisseur à partir de l'URL
                match = re.search(r'fournisseur=(\d+)', response.url)
                if match:
                    item['glass_supplier_id'] = match.group(1)
                else:
                    self.log(f"Failed to extract glass_supplier_id from URL: {response.url}", level=logging.ERROR)
                    continue  # Ignore cette ligne si l'ID n'est pas trouvé

                self.log(f"Extracted item: {item}", level=logging.DEBUG)
                yield item

