# Module API EngraveDetect

## Description
Le module API fournit une interface REST complète pour la gestion des verres optiques et leurs caractéristiques, ainsi que la détection des gravures. Il est construit avec FastAPI et suit une architecture modulaire.

## Architecture

### Structure du Module
```
api/
├── routes/                # Points d'entrée de l'API
│   ├── detection.py      # Route de détection
│   ├── fournisseurs.py   # Routes fournisseurs
│   ├── gammes.py         # Routes gammes
│   ├── materiaux.py      # Routes matériaux
│   ├── series.py         # Routes séries
│   ├── traitements.py    # Routes traitements
│   └── verres.py         # Routes verres
├── auth/                 # Authentification
│   ├── auth.py          # Logique JWT
│   └── dependencies.py   # Dépendances auth
├── dependencies/         # Dépendances partagées
│   ├── database.py      # Session DB
│   └── security.py      # Sécurité
└── tests/               # Tests
    ├── integration/     # Tests d'intégration
    └── unit/           # Tests unitaires
```

## Spécifications Techniques

### Configuration FastAPI
```python
# main.py
app = FastAPI(
    title="API Verres",
    description="API de gestion des verres optiques",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
app.add_middleware(
    SlowAPIMiddleware,
    rate_limit="100/minute"
)
```

### Authentification JWT
```python
# auth.py
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

## Routes API

### Route de Détection
```python
@router.post("/detect", response_model=DetectionResponse)
async def detect_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Détecte un symbole dans une image
    
    Args:
        file: Image à analyser (PNG, JPG, JPEG)
        current_user: Utilisateur authentifié
        
    Returns:
        DetectionResponse: Résultat de la détection
    """
```

### Routes CRUD Standard
```python
@router.get("/{id}", response_model=VerreResponse)
async def read_verre(
    id: int,
    db: Session = Depends(get_db)
):
    """Récupère un verre par son ID"""
    
@router.post("/", response_model=VerreResponse)
async def create_verre(
    verre: VerreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crée un nouveau verre"""
```

## Modèles de Données

### Pydantic Models
```python
class VerreBase(BaseModel):
    nom: str
    indice: float
    fournisseur_id: int
    
    class Config:
        orm_mode = True

class VerreCreate(VerreBase):
    pass

class VerreResponse(VerreBase):
    id: int
    created_at: datetime
```

### Validation
```python
class VerreValidator:
    @validator("indice")
    def validate_indice(cls, v):
        if not 1.0 <= v <= 2.0:
            raise ValueError("L'indice doit être entre 1.0 et 2.0")
        return v
```

## Sécurité

### Middleware de Sécurité
```python
# security.py
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### Rate Limiting
```python
# rate_limit.py
RATE_LIMIT_CONFIG = {
    "default": "100/minute",
    "/api/detect": "10/minute",
    "/api/token": "5/minute"
}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    endpoint = request.url.path
    limit = RATE_LIMIT_CONFIG.get(endpoint, RATE_LIMIT_CONFIG["default"])
    # ...
```

## Performance

### Optimisations
1. Cache Redis
```python
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": True
}

@router.get("/{id}", response_model=VerreResponse)
async def read_verre(id: int, cache: Redis = Depends(get_redis)):
    cache_key = f"verre:{id}"
    if cached := await cache.get(cache_key):
        return json.loads(cached)
    # ...
```

2. Pagination
```python
@router.get("/", response_model=Page[VerreResponse])
async def list_verres(
    pagination: Params = Depends(),
    db: Session = Depends(get_db)
):
    return paginate(db.query(Verre), pagination)
```

### Métriques
- Temps réponse moyen: <100ms
- Latence P95: 200ms
- Requêtes/sec: 1000
- Taux d'erreur: <0.1%

## Tests

### Tests Unitaires
```python
# test_routes.py
def test_create_verre(client, auth_headers):
    response = client.post(
        "/api/verres/",
        json={
            "nom": "Test",
            "indice": 1.5,
            "fournisseur_id": 1
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["nom"] == "Test"
```

### Tests d'Intégration
```python
# test_integration.py
def test_verre_workflow(client, auth_headers):
    # Create
    verre_data = {"nom": "Test", "indice": 1.5}
    response = client.post("/api/verres/", json=verre_data, headers=auth_headers)
    verre_id = response.json()["id"]
    
    # Read
    response = client.get(f"/api/verres/{verre_id}")
    assert response.status_code == 200
    
    # Update
    response = client.put(
        f"/api/verres/{verre_id}",
        json={"indice": 1.6},
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Delete
    response = client.delete(f"/api/verres/{verre_id}", headers=auth_headers)
    assert response.status_code == 204
```

## Monitoring

### Logging
```python
# Configuration logging
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'api.log',
            'formatter': 'detailed'
        }
    },
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(levelname)s [%(name)s] %(message)s'
        }
    },
    'loggers': {
        'api': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        }
    }
}
```

### Métriques Prometheus
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## Maintenance

### Tâches Quotidiennes
1. Vérification des logs
2. Monitoring performances
3. Vérification sécurité
4. Backup configuration

### Tâches Hebdomadaires
1. Analyse des erreurs
2. Optimisation routes
3. Mise à jour docs
4. Tests de charge

### Tâches Mensuelles
1. Revue sécurité
2. Mise à jour dépendances
3. Optimisation cache
4. Archivage logs

## Dépendances

### Requirements
```
fastapi>=0.68.0
uvicorn>=0.15.0
python-jose>=3.3.0
passlib>=1.7.4
python-multipart>=0.0.5
sqlalchemy>=1.4.23
redis>=4.0.2
prometheus-client>=0.11.0
```

### Compatibilité
- Python: 3.8+
- OS: Linux, Windows, macOS
- RAM: 2GB minimum
- CPU: 2 cores minimum

## Troubleshooting

### Problèmes Courants
1. Erreurs 5xx
   - Vérifier logs
   - Checker dépendances
   - Monitorer ressources

2. Latence élevée
   - Analyser requêtes
   - Optimiser cache
   - Vérifier DB

3. Erreurs auth
   - Vérifier tokens
   - Checker config
   - Logs sécurité

## Références

### Documentation
- FastAPI Documentation
- OpenAPI Specification
- JWT RFC 7519
- SQLAlchemy Docs

### Outils
- Swagger UI
- ReDoc
- Postman
- HTTPie

## Points d'Entrée de l'API

### Détection (`/api/detect`)
- POST `/api/detect` : Détecte le symbole dans une image
  - Accepte une image au format PNG, JPG, JPEG, GIF, BMP ou TIFF
  - Retourne le symbole détecté avec un score de confiance
  - Formats de réponse :
    ```json
    {
      "image_path": "string",
      "predicted_symbol": "string",
      "similarity_score": float,
      "is_confident": boolean,
      "message": "string"
    }
    ```

### Fournisseurs (`/api/fournisseurs`)
- GET `/api/fournisseurs` : Liste tous les fournisseurs
- GET `/api/fournisseurs/{id}` : Récupère un fournisseur spécifique
- POST `/api/fournisseurs` : Crée un nouveau fournisseur
- PUT `/api/fournisseurs/{id}` : Met à jour un fournisseur
- DELETE `/api/fournisseurs/{id}` : Supprime un fournisseur

### Matériaux (`/api/materiaux`)
- GET `/api/materiaux` : Liste tous les matériaux
- GET `/api/materiaux/{id}` : Récupère un matériau spécifique
- POST `/api/materiaux` : Crée un nouveau matériau
- PUT `/api/materiaux/{id}` : Met à jour un matériau
- DELETE `/api/materiaux/{id}` : Supprime un matériau

### Gammes (`/api/gammes`)
- GET `/api/gammes` : Liste toutes les gammes
- GET `/api/gammes/{id}` : Récupère une gamme spécifique
- POST `/api/gammes` : Crée une nouvelle gamme
- PUT `/api/gammes/{id}` : Met à jour une gamme
- DELETE `/api/gammes/{id}` : Supprime une gamme

### Séries (`/api/series`)
- GET `/api/series` : Liste toutes les séries
- GET `/api/series/{id}` : Récupère une série spécifique
- POST `/api/series` : Crée une nouvelle série
- PUT `/api/series/{id}` : Met à jour une série
- DELETE `/api/series/{id}` : Supprime une série

### Traitements (`/api/traitements`)
- GET `/api/traitements` : Liste tous les traitements
- GET `/api/traitements/{id}` : Récupère un traitement spécifique
- POST `/api/traitements` : Crée un nouveau traitement
- PUT `/api/traitements/{id}` : Met à jour un traitement
- DELETE `/api/traitements/{id}` : Supprime un traitement

### Verres (`/api/verres`)
- GET `/api/verres` : Liste tous les verres
- GET `/api/verres/{id}` : Récupère un verre spécifique
- POST `/api/verres` : Crée un nouveau verre
- PUT `/api/verres/{id}` : Met à jour un verre
- DELETE `/api/verres/{id}` : Supprime un verre

## Authentification

Le module utilise une authentification JWT (JSON Web Token) pour sécuriser les endpoints protégés.
- Routes publiques : GET, POST `/api/detect`
- Routes protégées : POST, PUT, DELETE (sauf `/api/detect`)

### Configuration de l'Authentification

Les variables d'environnement suivantes sont requises :
- `JWT_SECRET_KEY` : Clé secrète pour la signature des tokens
- `JWT_ALGORITHM` : Algorithme de signature (défaut: "HS256")
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` : Durée de validité du token en minutes (défaut: 30)
- `ADMIN_USERNAME` : Nom d'utilisateur administrateur
- `ADMIN_PASSWORD` : Mot de passe administrateur

## Modèles de Données

### DetectionResponse
```python
class DetectionResponse(BaseModel):
    image_path: str
    predicted_symbol: Optional[str]
    similarity_score: float
    is_confident: bool
    message: str
```

### FournisseurBase
```python
class FournisseurBase(BaseModel):
    nom: str
```

### MateriauBase
```python
class MateriauBase(BaseModel):
    nom: str
```

### GammeBase
```python
class GammeBase(BaseModel):
    nom: str
```

### SerieBase
```python
class SerieBase(BaseModel):
    nom: str
```

### TraitementBase
```python
class TraitementBase(BaseModel):
    nom: str
    type: str  # 'protection' ou 'photochromique'
```

### VerreBase
```python
class VerreBase(BaseModel):
    nom: Optional[str]
    variante: Optional[str]
    hauteur_min: Optional[int]
    hauteur_max: Optional[int]
    indice: Optional[float]
    url_gravure: Optional[str]
    url_source: Optional[str]
    fournisseur_id: Optional[int]
    materiau_id: Optional[int]
    gamme_id: Optional[int]
    serie_id: Optional[int]
```

## Tests

Le module inclut une suite de tests complète utilisant pytest :
- Tests unitaires pour chaque route
- Tests d'intégration avec la base de données
- Tests des cas d'erreur et des validations
- Tests de l'authentification
- Tests de détection d'images

Pour exécuter les tests :
```bash
pytest api/tests/
```

### Tests de Détection
Les tests de détection couvrent :
- Détection réussie avec haute confiance
- Détection avec faible confiance
- Gestion des formats de fichiers invalides
- Gestion des images corrompues
- Tests des différentes extensions d'images

## Documentation API

Documentation interactive disponible sur :
- Swagger UI : `/docs`
- ReDoc : `/redoc`

## Monitoring et Maintenance

1. **Logging**
   - Logs détaillés des requêtes
   - Traçage des erreurs
   - Métriques de performance
   - Alertes automatiques

2. **Maintenance**
   - Backups réguliers
   - Mises à jour de sécurité
   - Monitoring des performances
   - Gestion des versions 