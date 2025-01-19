import os
import subprocess
import time
import re
from importlib import import_module

def ensure_directories():
   """Crée les dossiers nécessaires s'ils n'existent pas."""
   os.makedirs('logs', exist_ok=True)
   os.makedirs('datalake/staging/data', exist_ok=True)

def get_fournisseur_id(url):
   """Extrait l'ID du fournisseur de l'URL."""
   match = re.search(r'fournisseur=(\d+)', url)
   if match:
       return match.group(1)
   # Pour les URLs du type /fournisseur/XXXX-nom
   match = re.search(r'fournisseur/(\d+)', url)
   return match.group(1) if match else None

def check_output_files(spider_name, start_urls):
   """Vérifie que chaque URL a généré son fichier CSV."""
   missing_files = []
   for url in start_urls:
       fournisseur_id = get_fournisseur_id(url)
       if fournisseur_id:
           expected_file = f"datalake/staging/data/fournisseur_{fournisseur_id}.csv"
           if not os.path.exists(expected_file):
               missing_files.append((url, fournisseur_id))
   return missing_files

def run_spider(spider_name):
   """Execute un spider et attend sa completion."""
   print(f"\n{'='*50}")
   print(f"Lancement de : {spider_name}")
   print(f"{'='*50}")
   
   try:
       # Lance le spider avec capture des sorties et timeout plus long
       process = subprocess.run(
           ['scrapy', 'crawl', spider_name],
           text=True,
           capture_output=True,
           timeout=3600  # 1 heure de timeout
       )
       
       # Affiche la sortie du spider
       print("Sortie du spider:")
       print(process.stdout)
       
       if process.stderr:
           print("Erreurs du spider:")
           print(process.stderr)

       # Vérifie si le spider a réussi
       if process.returncode != 0:
           print(f"Le spider {spider_name} a échoué avec le code {process.returncode}")
           return False

       # Importe le spider pour vérifier ses start_urls
       spider_module = import_module(f"scrapers.spiders.{spider_name}")
       spider_class = getattr(spider_module, ''.join(word.capitalize() for word in spider_name.split('_')))
       spider_instance = spider_class()
       
       # Vérifie les fichiers manquants
       missing_files = check_output_files(spider_name, spider_instance.start_urls)
       if missing_files:
           print(f"\nFichiers manquants pour {spider_name}:")
           for url, fournisseur_id in missing_files:
               print(f"- URL: {url} (fournisseur_{fournisseur_id}.csv)")
           return False
           
       # Attendre entre les spiders
       time.sleep(10)  # 10 secondes de pause entre les spiders
       return True
       
   except subprocess.TimeoutExpired:
       print(f"Timeout dépassé pour {spider_name}")
       return False
   except subprocess.CalledProcessError as e:
       print(f"Erreur lors de l'exécution de {spider_name}:")
       print(e.stderr)
       return False
   except Exception as e:
       print(f"Erreur inattendue pour {spider_name}: {str(e)}")
       return False

def run_all_spiders():
   """Lance tous les spiders séquentiellement."""
   ensure_directories()
   
   spiders = [
       'glass_spider_full_xpath',
       'glass_spider_hoya',
       'glass_spider_indo_optical',
       'glass_spider_optovision',
       'glass_spider_particular',
       'glass_spider'
   ]
   
   failed_spiders = []
   
   for spider in spiders:
       print(f"\nDémarrage de {spider}")
       if not run_spider(spider):
           failed_spiders.append(spider)
           print(f"Échec pour {spider}")
           time.sleep(10)  # 10 secondes de pause après un échec
       else:
           print(f"Succès pour {spider}")
   
   # Afficher le résumé
   print("\nRésumé de l'exécution :")
   print(f"Total spiders : {len(spiders)}")
   print(f"Réussis : {len(spiders) - len(failed_spiders)}")
   print(f"Échoués : {len(failed_spiders)}")
   
   if failed_spiders:
       print("\nSpiders en échec :")
       for spider in failed_spiders:
           print(f"- {spider}")

if __name__ == '__main__':
   run_all_spiders()