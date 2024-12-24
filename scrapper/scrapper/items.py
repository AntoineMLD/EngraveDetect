import scrapy


class EngravingItem(scrapy.Item):
    """
    Définition des champs pour les éléments extraits par le spider.
    """
    category = scrapy.Field()              # Catégorie du verre (e.g., progressif, unifocal)
    glass_name = scrapy.Field()            # Nom complet du verre
    nasal_engraving = scrapy.Field()       # Gravure nasale (lien vers une image ou texte)
    glass_index = scrapy.Field()           # Indice du verre (e.g., 1.50, 1.67)
    material = scrapy.Field()              # Matériau du verre (e.g., ORG, MIN)
    glass_supplier_id = scrapy.Field()     # ID numérique du fournisseur
    supplier_name = scrapy.Field()         # Nom du fournisseur (ajouté par le pipeline)
