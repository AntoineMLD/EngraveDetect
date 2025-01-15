import pandas as pd
import re
import os

# Défini le chemin du fichier
file_path = 'C:/Users/antoi/Documents/Projets/Projet Certif/EngraveDetect/scrapers/datalake/staging/data/staging_scrapping.csv'

# Vérifie si le fichier existe
if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file {file_path} does not exist.")

# Lit le fichier CSV
df = pd.read_csv(file_path)

# Fonction pour nettoyer le nom du verre
def clean_glass_name(name):
    """
    Nettoie le nom du verre en supprimant les caractères spéciaux, en remplaçant les espaces multiples par un seul espace, et en remplaçant les caractères inutiles.
    """
    name = name.lower()
    name = re.sub(r'[^a-zA-Z0-9\s/]', '', name)
    name = ' '.join(name.split())
    name = name.replace(' / ', ' ')
    name = name.replace('/', '_')
    name = name.replace(' ', '_')
    name = name.strip()
    return name

def clean_category(category):
    """
    Nettoie la catégorie en supprimant les caractères spéciaux, en remplaçant les espaces multiples par un seul espace, et en remplaçant les caractères inutiles.
    """
    category = category.lower()
    category = category.replace(' ', '_')
    category = category.replace('(', '')        
    category = category.replace(')', '')
    category = category.replace('_/_', '_')
    category = category.strip()
    return category

def clean_material(material):
    """
    Nettoie le matériau en supprimant les caractères spéciaux, en remplaçant les espaces multiples par un seul espace, et en remplaçant les caractères inutiles.
    """
    material = material.lower()
    material = material.strip()
    return material

def clean_glass_supplier_name(glass_supplier_name):
    """
    Nettoie le nom du supplier en supprimant les caractères spéciaux, en remplaçant les espaces multiples par un seul espace, et en remplaçant les caractères inutiles.
    """
    glass_supplier_name = glass_supplier_name.lower()
    glass_supplier_name = glass_supplier_name.strip()
    glass_supplier_name = glass_supplier_name.replace(' ', '_')
    return glass_supplier_name  



def clean_nasal_engraving(nasal_engraving):
    """ Si nasal_engraving ne commence pas par https:// alors applique des fonctions pour le nettoyer """
    if pd.isna(nasal_engraving):
        return ''
    if not nasal_engraving.startswith('https://'):
        nasal_engraving = nasal_engraving.lower()
        nasal_engraving = nasal_engraving.strip()
        nasal_engraving = nasal_engraving.replace('/', ' ')
        
    return nasal_engraving


# Applique les fonctions de nettoyage
df['glass_name'] = df['glass_name'].apply(clean_glass_name)
df['category'] = df['category'].apply(clean_category)
df['material'] = df['material'].apply(clean_material)
df['glass_supplier_name'] = df['glass_supplier_name'].apply(clean_glass_supplier_name)
df['nasal_engraving'] = df['nasal_engraving'].apply(clean_nasal_engraving)

# Supprime l'id du supplier 
df = df.drop(columns=['glass_supplier_id'])

# Remplace le contenu de la colonne image_engraving par True si pas de données alors False
df['image_engraving'] = df['image_engraving'].apply(lambda x: True if pd.notna(x) else False)

# Supprime les doublons
df = df.drop_duplicates()

# Écrit le DataFrame nettoyé dans un nouveau fichier CSV
df.to_csv('C:/Users/antoi/Documents/Projets/Projet Certif/EngraveDetect/scrapers/datalake/enhanced/enhanced_scrapping.csv', index=False)   