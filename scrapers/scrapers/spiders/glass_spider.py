import scrapy
import re
import logging
from scrapers.items import ScrapersItem
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider


class GlassSpider(scrapy.Spider):
    name = "glass_spider"
    allowed_domains = ["www.france-optique.com"]

    # Ajout des URLs de tous les fournisseurs
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
        self.log(f"Analyse de la page: {response.url}", level=logging.INFO)

        # Méthode 1 : Extraction classique des catégories et des gravures
        category_elements = response.xpath('//div[@class="row tr group"]')
        if category_elements:
            self.log("Using Method 1: Extraction basée sur les catégories", level=logging.INFO)
            for category in category_elements:
                category_name = category.xpath('./text()').get()
                if category_name:
                    category_name = category_name.strip()
                else:
                    self.log(f"Le nom de la catégorie est manquant sur la page: {response.url}", level=logging.WARNING)
                    continue

                engraving_rows = category.xpath('./following-sibling::div[@class="row tr"]')
                if not engraving_rows:
                    self.log(f"Aucune gravure trouvée pour la catégorie: {category_name}", level=logging.WARNING)
                    continue

                for engraving_row in engraving_rows:
                    yield self.extract_engraving(engraving_row, category_name, response.url)

        else:
            # Méthode 2 : Extraction sans catégories spécifiques
            self.log("Using Method 2: Extraction directe des gravures", level=logging.INFO)
            engraving_rows = response.xpath('//div[contains(@class, "row tr")]')
            for engraving_row in engraving_rows:
                yield self.extract_engraving(engraving_row, category_name=None, url=response.url)

        # Méthode 3 : Extraction depuis les collapsibles pour mobiles
        collapsibles = response.xpath('//ul[@class="collapsible"]/li')
        if collapsibles:
            self.log("Using Method 3: Extraction depuis les collapsibles pour mobiles", level=logging.INFO)
            for collapsible in collapsibles:
                category_name = collapsible.xpath('./preceding-sibling::div[@class="row tr group"][1]/text()').get()
                if category_name:
                    category_name = category_name.strip()
                else:
                    category_name = "Uncategorized"

                engraving_rows = collapsible.xpath('.//div[contains(@class, "collapsible-body")]')
                for engraving_row in engraving_rows:
                    yield self.extract_collapsible_engraving(engraving_row, category_name, response.url)

    def extract_engraving(self, engraving_row, category_name, url):
        """Extrait les details d'une gravure."""
        item = ScrapersItem()
        item['category'] = category_name or "Uncategorized"

        item['glass_name'] = engraving_row.xpath(
            './/div[contains(@class, "col s4 m4")]/p/text()'
        ).get()

        item['nasal_engraving'] = engraving_row.xpath(
        './/div[contains(@class, "col s1 m1")][2]/img[contains(@src, "nasal")]/@src'
        ).get() or engraving_row.xpath(
            './/td[contains(@class, "col s6")]/img[contains(@src, "nasal")]/@src'
        ).get() or engraving_row.xpath(
            './/td[contains(@class, "col s6")]/p[@class="gravure_txt"]/b/text()'
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
        match = re.search(r'fournisseur=(\d+)', url)
        if match:
            item['glass_supplier_id'] = match.group(1)
        else:
            self.log(f"Echec de l'extraction de l'ID du fournisseur à partir de l'URL: {url}", level=logging.ERROR)

        self.log(f"Extracted item: {item}", level=logging.DEBUG)
        return item

    def extract_collapsible_engraving(self, collapsible_body, category_name, url):
        """Extrait les details d'un collapsible pour la vue mobile."""
        item = ScrapersItem()
        item['category'] = category_name or "Uncategorized"

        item['glass_name'] = collapsible_body.xpath(
            './/div[contains(@class, "row") and .//div[text()="NOM DU VERRE"]]/div[@class="td col s6"]/text()'
        ).get()

        item['nasal_engraving'] = collapsible_body.xpath(
            './/div[contains(@class, "row") and .//img[contains(@src, "nasal")]]/div[@class="td col s6"]/img[contains(@src, "nasal")]/@src'
        ).get() or collapsible_body.xpath(
            './/div[contains(@class, "row") and .//div[text()="NASAL"]]/div[@class="td col s6"]/p/b/text()'
        ).get()

        item['glass_index'] = collapsible_body.xpath(
            './/div[contains(@class, "row") and .//div[text()="INDICE"]]/div[@class="td col s6"]/text()'
        ).get()

        item['material'] = collapsible_body.xpath(
            './/div[contains(@class, "row") and .//div[text()="MATIÈRE"]]/div[@class="td col s6"]/text()'
        ).get()

        # Extraction de l'ID du fournisseur à partir de l'URL
        match = re.search(r'fournisseur=(\d+)', url)
        if match:
            item['glass_supplier_id'] = match.group(1)
        else:
            self.log(f"Echec de l'extraction de l'ID du fournisseur à partir de l'URL: {url}", level=logging.ERROR)

        self.log(f"Extrait l'item à partir du collapsible: {item}", level=logging.DEBUG)
        return item