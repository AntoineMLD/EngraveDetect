import scrapy


class ScrapersItem(scrapy.Item):
    category = scrapy.Field()
    glass_name = scrapy.Field()
    nasal_engraving = scrapy.Field()
    glass_index = scrapy.Field()
    material = scrapy.Field()
    glass_supplier_id = scrapy.Field()
    glass_supplier_name = scrapy.Field()
    image_engraving = scrapy.Field()
