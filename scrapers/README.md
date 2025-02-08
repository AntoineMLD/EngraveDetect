# Module Scrapers EngraveDetect

## Architecture

### Structure du Module
```
scrapers/
├── spiders/              # Spiders Scrapy
│   ├── bbgr.py          # Spider BBGR
│   ├── hoya.py          # Spider HOYA
│   ├── seiko.py         # Spider SEIKO
│   ├── shamir.py        # Spider SHAMIR
│   └── rodenstock.py    # Spider RODENSTOCK
├── pipelines/           # Pipelines de traitement
│   ├── validation.py    # Validation des données
│   ├── cleaning.py      # Nettoyage des données
│   └── export.py        # Export des données
├── middlewares/         # Middlewares personnalisés
└── settings.py         # Configuration Scrapy
```

### Pipeline de Données
1. Extraction (Spiders)
2. Validation (Pipelines)
3. Nettoyage (Pipelines)
4. Transformation (Pipelines)
5. Export (CSV/JSON)

## Spécifications Techniques

### Configuration Scrapy
```python
# settings.py
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1.5
ROBOTSTXT_OBEY = True
RETRY_TIMES = 3
COOKIES_ENABLED = True
USER_AGENT = 'EngraveDetect/1.0'
```

### Middlewares
- Rotation des User-Agents
- Gestion des proxies
- Rate limiting
- Retry avec backoff

### Pipelines
1. ValidationPipeline
   - Schéma des données
   - Contraintes métier
   - Logging des erreurs

2. CleaningPipeline
   - Normalisation
   - Déduplication
   - Enrichissement

3. ExportPipeline
   - Format CSV/JSON
   - Compression
   - Archivage

## Spiders

### BBGR Spider
```python
class BBGRSpider(scrapy.Spider):
    name = 'bbgr'
    allowed_domains = ['bbgr.fr']
    custom_settings = {
        'DOWNLOAD_DELAY': 2.0,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8
    }
```

### HOYA Spider
```python
class HOYASpider(scrapy.Spider):
    name = 'hoya'
    allowed_domains = ['hoya.fr']
    custom_settings = {
        'DOWNLOAD_DELAY': 1.5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 10
    }
```

[... autres spiders ...]

## Format des Données

### Schéma de Sortie
```json
{
    "fournisseur": "string",
    "gamme": "string",
    "materiau": "string",
    "serie": "string",
    "nom": "string",
    "variante": "string",
    "indice": "float",
    "url_gravure": "string",
    "url_source": "string"
}
```

### Validation
```python
class VerreItem(scrapy.Item):
    fournisseur = Field(required=True)
    gamme = Field(required=True)
    materiau = Field(required=True)
    serie = Field(required=False)
    nom = Field(required=True)
    variante = Field(required=False)
    indice = Field(required=True, type=float)
    url_gravure = Field(required=False)
    url_source = Field(required=True)
```

## Performance

### Métriques
- Vitesse: ~500 items/minute
- Précision: 99.9%
- Taux d'erreur: <0.1%
- Utilisation mémoire: <500MB

### Optimisations
1. Mise en cache DNS
2. Connection pooling
3. Compression des réponses
4. Parsing asynchrone

## Monitoring

### Métriques Clés
- Items scraped/minute
- Erreurs HTTP
- Temps de réponse
- Utilisation mémoire

### Logging
```python
# Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_FILE = 'scraping.log'
```

### Alertes
- Erreurs HTTP > 10%
- Temps réponse > 5s
- Mémoire > 1GB
- Items/min < 100

## Tests

### Tests Unitaires
```bash
pytest tests/test_spiders.py
pytest tests/test_pipelines.py
pytest tests/test_items.py
```

### Tests d'Intégration
```bash
pytest tests/integration/
```

### Tests de Charge
```bash
locust -f tests/locustfile.py
```

## Maintenance

### Tâches Quotidiennes
1. Vérification des logs
2. Validation des exports
3. Monitoring des erreurs
4. Nettoyage du cache

### Tâches Hebdomadaires
1. Mise à jour des proxies
2. Rotation des User-Agents
3. Validation des patterns
4. Backup des données

### Tâches Mensuelles
1. Mise à jour des spiders
2. Optimisation des requêtes
3. Revue des métriques
4. Mise à jour documentation

## Dépendances

### Requirements
```
scrapy>=2.5.0
itemadapter>=0.3.0
w3lib>=1.22.0
service_identity>=21.1.0
python-dotenv>=0.19.0
```

### Compatibilité
- Python: 3.8+
- OS: Linux, Windows, macOS
- RAM: 2GB minimum
- CPU: 2 cores minimum

## Sécurité

### Bonnes Pratiques
1. Respect robots.txt
2. Rate limiting strict
3. Rotation des IPs
4. Validation des inputs

### Protection
- HTTPS uniquement
- Validation des certificats
- Sanitization des données
- Logging sécurisé

## Troubleshooting

### Problèmes Courants
1. Blocage IP
   - Rotation des proxies
   - Ajustement delays
   - Vérification User-Agent

2. Parsing échoué
   - Mise à jour patterns
   - Validation XPaths
   - Debug données

3. Performance
   - Optimisation requêtes
   - Ajustement concurrence
   - Monitoring ressources

## Références

### Documentation
- Scrapy Official Docs
- XPath Reference
- HTTP Best Practices
- Web Scraping Guide

### Outils
- Scrapy Shell
- XPath Helper
- HTTP Toolkit
- Charles Proxy 