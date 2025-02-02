# Module API

## Description
Le module API fournit une interface REST complète pour la gestion des verres optiques et leurs caractéristiques. Il est construit avec FastAPI et suit une architecture modulaire.

## Structure du Module

```
api/
├── auth/                  # Gestion de l'authentification
├── dependencies/         # Dépendances partagées
├── routes/              # Points d'entrée de l'API
├── tests/              # Tests unitaires
└── main.py            # Point d'entrée principal
```

## Points d'Entrée de l'API

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

Le module utilise une authentification JWT (JSON Web Token) pour sécuriser les endpoints protégés. Les routes en lecture seule (GET) sont publiques, tandis que les routes de modification (POST, PUT, DELETE) nécessitent une authentification.

### Configuration de l'Authentification

Les variables d'environnement suivantes sont requises :
- `JWT_SECRET_KEY` : Clé secrète pour la signature des tokens
- `JWT_ALGORITHM` : Algorithme de signature (défaut: "HS256")
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` : Durée de validité du token en minutes (défaut: 30)
- `ADMIN_USERNAME` : Nom d'utilisateur administrateur
- `ADMIN_PASSWORD` : Mot de passe administrateur

## Modèles de Données

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

Le module inclut une suite de tests complète utilisant pytest. Les tests couvrent :
- Tests unitaires pour chaque route
- Tests d'intégration avec la base de données
- Tests des cas d'erreur et des validations
- Tests de l'authentification

Pour exécuter les tests :
```bash
pytest api/tests/
```

## Dépendances Principales

- FastAPI : Framework web moderne et rapide
- SQLAlchemy : ORM pour la gestion de la base de données
- Pydantic : Validation des données et sérialisation
- python-jose : Gestion des JWT
- passlib : Hachage des mots de passe
- pytest : Framework de test

## Bonnes Pratiques

1. **Gestion des Erreurs**
   - Utilisation cohérente des codes HTTP
   - Messages d'erreur descriptifs
   - Rollback automatique en cas d'erreur de base de données

2. **Validation des Données**
   - Validation stricte des entrées avec Pydantic
   - Contraintes de base de données
   - Vérifications métier personnalisées

3. **Sécurité**
   - Authentification JWT
   - Protection contre les injections SQL via ORM
   - Validation des entrées
   - Messages d'erreur sécurisés

4. **Performance**
   - Utilisation de lazy loading
   - Pagination des résultats
   - Optimisation des requêtes SQL 