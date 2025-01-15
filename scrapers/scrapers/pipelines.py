import os
import requests
from itemadapter import ItemAdapter
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

class ScrapersPipeline:
    def __init__(self):
        load_dotenv()
        self.azure_connection_string = os.getenv("AZURE_CONNECTION_STRING")

        # vérifie la connexion azure
        if not self.azure_connection_string:
            raise RuntimeError("Vérifier .env pour la connection Azure.")

        # Initialise Azure Blob Storage client
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.azure_connection_string)
            self.container_name = "raw-data"
        except Exception as e:
            raise RuntimeError(f"Échec de l'initialisation du client Azure Blob : {e}")

        
        self.local_output_file = "datalake/staging/data/staging_scrapping.csv"
        self.local_image_path = "datalake/staging/media"
        self.items = []

        # Créer les dossiers
        os.makedirs(os.path.dirname(self.local_output_file), exist_ok=True)
        os.makedirs(self.local_image_path, exist_ok=True)

        # Dictionnaire des fournisseurs
        self.supplier_mapping = {
            2399: "ADN OPTIS", # pas scrappé
            1344: "BBGR OPTIQUE", # pas scrappé
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

    def open_spider(self, spider):
        """Initialise les ressources à l'ouverture du spider."""
        spider.logger.info("Pipeline initialisé et prêt.")

    def process_item(self, item, spider):
        """Traite chaque élément collecté par le spier."""
        # Valide et mappe l'ID du fournisseur
        supplier_id = item.get("glass_supplier_id")
        try:
            supplier_id = int(supplier_id)
        except ValueError:
            spider.logger.warning(f"Le supplier ID est invalide: {supplier_id}")
            item["glass_supplier_name"] = "Unknown Supplier"
        else:
            item["glass_supplier_name"] = self.supplier_mapping.get(supplier_id, "Unknown Supplier")

        # valide la catégorie
        if not item.get('category'):
            spider.logger.warning(f"Catégorie manquante pour: {item['glass_name']}")
            item['category'] = "Non spécifié"

        # vérifie l'image de la gravure
        image_url = item.get("nasal_engraving")
        if image_url and image_url.startswith(("http", "https")):
            try:
                # télécharge l'image
                image_name = os.path.basename(image_url)
                local_image_path = os.path.join(self.local_image_path, image_name)

                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    with open(local_image_path, 'wb') as out_file:
                        for chunk in response.iter_content(chunk_size=8192):
                            out_file.write(chunk)
                    item["image_engraving"] = local_image_path
                    spider.logger.info(f"Downloaded image: {image_url}")

                    # télécharge l'image vers Azure Blob Storage
                    try:
                        blob_client = self.blob_service_client.get_blob_client(
                            container=self.container_name,
                            blob=f"staging/media/{image_name}"
                        )
                        with open(local_image_path, "rb") as data:
                            blob_client.upload_blob(data, overwrite=True)
                        spider.logger.info(f"Télécharge l'image vers Azure Blob Storage: {image_name}")
                    except Exception as e:
                        spider.logger.error(f"Impossible de télécharger l'image vers Azure Blob Storag: {e}")

                else:
                    spider.logger.error(f"Échec du téléchargement de l'image: {image_url}")
                    item["image_engraving"] = None
            except Exception as e:
                spider.logger.error(f"Erreur du téléchargement de l'image: {e}")
                item["image_engraving"] = None
        else:
            item["image_engraving"] = None

        # Ajoute un élément à la liste par batch
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        """Gére le traitement final lors de la fermeture du spider"""
        # Sauvegarde des données collectées dans un fichier CSV local
        try:
            if self.items:
                import csv
                with open(self.local_output_file, "w", newline='', encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=self.items[0].keys())
                    writer.writeheader()
                    writer.writerows(self.items)
                spider.logger.info("Les données ont été enregistrées avec succès dans un fichier CSV local.")
            else:
                spider.logger.warning("Aucun items à sauvegarder.")
        except Exception as e:
            spider.logger.error(f"Échec de l'enregistrement du fichier CSV local : {e}")

        # télécharge le fichier CSV vers Azure Blob Storage
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob="staging/staging_scrapping.csv"
            )
            with open(self.local_output_file, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            spider.logger.info("Données téléchargées avec succès vers Azure Blob Storage")
        except Exception as e:
            spider.logger.error(f"Échec du téléchargement des données vers Azure Blob Storage : {e}")