import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
import logging

class OpticalLensDataCleaner:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_image_url(self, html_str: str) -> str:
        """Extrait l'URL de l'image, que ce soit depuis HTML ou URL directe."""
        if pd.isna(html_str):
            return None
        if '<img' in html_str:
            # Format HTML du premier CSV
            soup = BeautifulSoup(html_str, 'html.parser')
            img_tag = soup.find('img')
            return img_tag['src'] if img_tag else None
        else:
            # Format URL directe du second CSV
            return html_str

    def clean_material(self, material: str) -> str:
        """Nettoie le matériau, qu'il soit en HTML ou en texte direct."""
        if pd.isna(material):
            return None
        if '<' in material:
            # Format HTML du premier CSV
            return BeautifulSoup(material, 'html.parser').get_text().strip()
        else:
            # Format texte direct du second CSV
            return material.strip()

    def process_glass_name(self, glass_name: str) -> dict:
        """Traite le nom du verre et retourne un dictionnaire avec le nom de base et les traitements."""
        if pd.isna(glass_name):
            return {'base_name': None, 'treatments': []}
        
        parts = [p.strip() for p in glass_name.split('/')]
        base_name = parts[0]
        treatments = [t.strip() for t in parts[1:]]
        
        return {
            'base_name': base_name,
            'treatments': '|'.join(treatments) if treatments else ''
        }

    def clean_supplier_name(self, supplier: str) -> str:
        """Nettoie le nom du fournisseur."""
        if pd.isna(supplier):
            return None
        return supplier.replace('Fournisseur : ', '').strip()

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie un DataFrame de verres optiques."""
        cleaned_df = pd.DataFrame()

        processed_names = df['glass_name'].apply(self.process_glass_name)
        cleaned_df['base_name'] = processed_names.apply(lambda x: x['base_name'])
        cleaned_df['treatments'] = processed_names.apply(lambda x: x['treatments'])

        cleaned_df['glass_index'] = df['glass_index']
        cleaned_df['material'] = df['material'].apply(self.clean_material)
        cleaned_df['supplier'] = df['glass_supplier_name'].apply(self.clean_supplier_name)
        cleaned_df['engraving_url'] = df['nasal_engraving'].apply(self.extract_image_url)
        cleaned_df['source_url'] = df['source_url']

        # Ajout du traitement pour image_engraving s'il existe
        if 'image_engraving' in df.columns:
            cleaned_df['local_image_path'] = df['image_engraving']

        return cleaned_df

    def process_and_save_file(self, input_path: Path, output_folder: Path):
        """
        Traite un fichier CSV et sauvegarde directement le résultat.
        
        Args:
            input_path: Chemin vers le fichier CSV à traiter
            output_folder: Dossier où sauvegarder le fichier nettoyé
        """
        try:
            # Création du dossier de sortie si nécessaire
            output_folder.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Traitement du fichier: {input_path.name}")
            
            # Lecture et nettoyage
            df = pd.read_csv(input_path)
            cleaned_df = self.clean_dataframe(df)
            
            # Sauvegarde
            output_path = output_folder / f"enhanced_{input_path.name}"
            cleaned_df.to_csv(output_path, index=False)
            self.logger.info(f"Fichier nettoyé sauvegardé: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de {input_path.name}: {str(e)}")
            raise

def main():
    cleaner = OpticalLensDataCleaner()
    
    # Obtention du chemin absolu du dossier racine du projet
    project_root = Path(__file__).parent.parent.parent
    
    # Construction des chemins absolus
    staging_folder = project_root / "scrapers" / "datalake" / "staging" / "data"
    enhanced_folder = project_root / "scrapers" / "datalake" / "enhanced" / "data"
    
    # Fichier à traiter
    first_file = "fournisseur_70.csv"
    input_file_path = staging_folder / first_file
    
    try:
        if not input_file_path.exists():
            raise FileNotFoundError(f"Le fichier {input_file_path} n'existe pas.")
            
        cleaner.process_and_save_file(input_file_path, enhanced_folder)
            
    except Exception as e:
        print(f"Une erreur est survenue : {str(e)}")

if __name__ == "__main__":
    main()