import os
import json
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
            raise RuntimeError("Azure connection string is missing. Check your .env file.")

        # Initialisation du client Azure Blob Storage
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.azure_connection_string)
            self.container_name = "raw-data"
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Azure Blob client: {e}")

        # Initialisation des fichiers de sortie
        self.local_output_file = "output_opticalspider.json"
        self.items = []

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

    def open_spider(self, spider):
        """Initialisation lors de l'ouverture du spider."""
        spider.logger.info("Pipeline initialized and ready.")

    def process_item(self, item, spider):
        """Traitement des éléments collectés par le spider."""
        # Vérification et mappage du fournisseur
        supplier_id = item.get("glass_supplier_id")
        try:
            supplier_id = int(supplier_id)  # Conversion en entier si nécessaire
        except ValueError:
            spider.logger.warning(f"Invalid supplier ID: {supplier_id}")
            item["glass_supplier_name"] = "Unknown Supplier"
        else:
            item["glass_supplier_name"] = self.supplier_mapping.get(supplier_id, "Unknown Supplier")

        # Ajout de l'élément dans la liste pour traitement groupé
        self.items.append(dict(item))  # Conversion en dictionnaire
        return item

    def close_spider(self, spider):
        """Traitement des éléments collectés lors de la fermeture du spider."""
        # Sauvegarde locale des données collectées
        try:
            with open(self.local_output_file, "w", encoding="utf-8") as f:
                json.dump(self.items, f, ensure_ascii=False, indent=4)
            spider.logger.info(f"Data successfully saved locally to {self.local_output_file}.")
        except Exception as e:
            spider.logger.error(f"Failed to save data locally: {e}")

        # Sauvegarde dans Azure Blob Storage
        try:
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob="scrapped_data/opticalspider.json")
            with open(self.local_output_file, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            spider.logger.info("Data successfully uploaded to Azure Blob Storage.")
        except Exception as e:
            spider.logger.error(f"Failed to save data to Azure Blob Storage: {e}")
