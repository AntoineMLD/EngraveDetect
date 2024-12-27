import os
import json
import re
import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from scrapy.exceptions import DropItem

class OpticalPipeline:
    def __init__(self):
        # Chargement des variables d'environnement depuis le fichier .env
        load_dotenv()
        self.azure_connection_string = os.getenv("AZURE_CONNECTION_STRING")

        # Vérification de la chaîne de connexion Azure
        if not self.azure_connection_string:
            raise RuntimeError("Azure connection est manquante. Vérifier .env file.")

        # Initialisation du client Azure Blob Storage
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.azure_connection_string)
            self.container_name = "raw-data"
        except Exception as e:
            raise RuntimeError(f"Echec d'initialisation Azure Blob client: {e}")

        # Initialisation des fichiers de sortie
        self.local_output_file = "output_opticalspider.json"
        self.local_image_path = "media/engraving_images/"
        self.items = []

        # Création des répertoires locaux si nécessaire
        os.makedirs(self.local_image_path, exist_ok=True)

        # Dictionnaire de mappage des fournisseurs
        self.supplier_mapping = {
            2399: "ADN OPTIS",
            1344: "BBGR OPTIQUE",
            70: "DIVEL FRANCE",
            521: "ESSILOR FRANCE",
            1488: "HEPHILENS",
            130: "HOYA VISION CARE FRANCE",
            1958: "INDO OPTICAL FRANCE",
            2217: "K OPTICAL",
            2532: "LEICA EYECARE",
            644: "MEGA OPTIC",
            1838: "MONT ROYAL",
            561: "NIKON VERRES OPTIQUES",
            711: "NOVACEL",
            2395: "OPHTALMIC COMPAGNIE",
            127: "OPTIC 200",
            659: "OPTISWWIS FRANCE",
            789: "OPTOVISION GMBH",
            2069: "RODENSTOCK",
            1407: "SEIKO OPTICAL France",
            2397: "SHAMIR FRANCE",
            2644: "VERRES KODAK",
            2414: "ZEISS VISION CARE FRANCE",
        }

    def normalize_glass_name(self, glass_name, glass_index):
        """
        Normalise le nom des verres en suivant les règles définies.
        """
        # Suppression des phrases entre parenthèses contenant des dates ou autres indications
        glass_name = re.sub(r'\(.*?\)', '', glass_name)

        # Suppression des indices déjà présents dans glass_index
        glass_name = re.sub(rf'\b{re.escape(glass_index)}\b', '', glass_name)
        
        # Suppression des années ou dates non pertinentes
        glass_name = re.sub(r'\b(20\d{2}|\b\d{2}\b)\b', '', glass_name)
        
        # Remplacement des plages numériques par un format standardisé
        glass_name = re.sub(r'(\d+)\s*[&/-]\s*(\d+)', r'\1_\2', glass_name)

        # Remplacement des virgules par des tirets
        glass_name = glass_name.replace(',', '-')

        # Nettoyage des caractères spéciaux et uniformisation
        glass_name = re.sub(r'[®™]', '', glass_name)  # Supprime les marques déposées
        glass_name = glass_name.replace('/', '-').replace('  ', ' ').strip()
        glass_name = re.sub(r'\s+', '-', glass_name.lower())  # Uniformise les espaces

        return glass_name.strip('-')

    def open_spider(self, spider):
        """Initialisation lors de l'ouverture du spider."""
        spider.logger.info("Pipeline initialisé et prêt.")

    def process_item(self, item, spider):
        """Traitement des éléments collectés par le spider."""
        # Vérification et mappage du fournisseur
        supplier_id = item.get("glass_supplier_id")
        try:
            supplier_id = int(supplier_id)
        except ValueError:
            spider.logger.warning(f"Invalid supplier ID: {supplier_id}")
            item["glass_supplier_name"] = "Unknown Supplier"
        else:
            item["glass_supplier_name"] = self.supplier_mapping.get(supplier_id, "Unknown Supplier")

        # Normalisation du nom des verres
        item['glass_name_normalized'] = self.normalize_glass_name(
            item.get('glass_name', ''),
            item.get('glass_index', '')
        )

        # Vérification de la catégorie
        if not item.get('category'):
            spider.logger.warning(f"Catégorie manquante pour l'item : {item['glass_name']}")
            item['category'] = "Non spécifié"

        # Gestion des images de gravure
        image_url = item.get("nasal_engraving")
        if image_url and image_url.startswith("http"):
            try:
                # Téléchargement de l'image
                image_name = f"{item['glass_name_normalized']}_{item['glass_index']}.jpg".replace(" ", "_").lower()
                local_image_path = os.path.join(self.local_image_path, image_name)

                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    with open(local_image_path, "wb") as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)

                    # Sauvegarde dans Azure Blob Storage
                    blob_client = self.blob_service_client.get_blob_client(
                        container=self.container_name,
                        blob=f"engraving_images/{image_name}"
                    )
                    with open(local_image_path, "rb") as data:
                        blob_client.upload_blob(data, overwrite=True)

                    item["image_engraving"] = local_image_path
                else:
                    spider.logger.warning(f"Echec du téléchargement de l'image : {image_url}")
                    item["image_engraving"] = None
            except Exception as e:
                spider.logger.error(f"erreur concernant l'image : {e}")
                item["image_engraving"] = None
        else:
            item["image_engraving"] = None

        # Ajout de l'élément dans la liste pour traitement groupé
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        """Traitement des éléments collectés lors de la fermeture du spider."""
        # Sauvegarde locale des données collectées
        try:
            with open(self.local_output_file, "w", encoding="utf-8") as f:
                json.dump(self.items, f, ensure_ascii=False, indent=4)
            spider.logger.info(f"Données sauvegardées avec succès localement dans {self.local_output_file}.")
        except Exception as e:
            spider.logger.error(f"Echec de sauvegarde locale pour : {e}")

        # Sauvegarde des métadonnées des images dans Azure Blob Storage
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob="scrapped_data/opticalspider.json"
            )
            with open(self.local_output_file, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            spider.logger.info("Données transmises avec succès vers l'azure blob storage.")
        except Exception as e:
            spider.logger.error(f"Echec de sauvegarde des données vers l'azure blob storage : {e}")
