import scrapy


class EngravingItem(scrapy.Item):
    category = scrapy.Field()          # Catégorie du verre (e.g., progressif)
    glass_name = scrapy.Field()        # Nom du verre
    nasal_engraving = scrapy.Field()   # Gravure nasale (texte ou image)
    glass_index = scrapy.Field()       # Indice du verre
    material = scrapy.Field()          # Matériau (e.g., ORG, MIN)
    glass_supplier_id = scrapy.Field() # ID numérique du fournisseur
    glass_supplier_name = scrapy.Field()  # Nom du fournisseur
