import scrapy


class ScrapersItem(scrapy.Item):
    glass_name = scrapy.Field()
    nasal_engraving = scrapy.Field()
    glass_index = scrapy.Field()
    material = scrapy.Field()
    glass_supplier_name = scrapy.Field()
    image_engraving = scrapy.Field()
