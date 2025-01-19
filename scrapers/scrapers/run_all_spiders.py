import os
import subprocess
import time

def ensure_logs_directory():
    # Créer le dossier logs s'il n'existe pas
    if not os.path.exists('logs'):
        os.makedirs('logs')
    # Créer le fichier scrapy.log s'il n'existe pas
    log_file = os.path.join('logs', 'scrapy.log')
    if not os.path.exists(log_file):
        open(log_file, 'a').close()

def run_all_spiders():
    # S'assurer que le dossier logs existe
    ensure_logs_directory()
    
    spiders = [
        'glass_spider_full_xpath',
        'glass_spider_hoya',
        'glass_spider_indo_optical',
        'glass_spider_optovision',
        'glass_spider_particular',
        'glass_spider'
    ]
    
    for spider in spiders:
        print(f"\n{'='*50}")
        print(f"Starting spider: {spider}")
        print(f"{'='*50}\n")
        
        try:
            subprocess.run(['scrapy', 'crawl', spider], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running spider {spider}: {e}")
        except Exception as e:
            print(f"Unexpected error with spider {spider}: {e}")
            
        time.sleep(2)  # Attendre 2 secondes entre chaque spider
        print(f"\nFinished spider: {spider}")

if __name__ == '__main__':
    run_all_spiders()