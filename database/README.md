# Module Base de Données EngraveDetect

## Architecture

### Structure du Module
```
database/
├── config/              # Configuration SQLAlchemy
│   ├── database.py     # Configuration connexion
│   └── settings.py     # Paramètres globaux
├── models/             # Modèles SQLAlchemy (ORM)
│   ├── verre.py       # Modèle Verre
│   ├── fournisseur.py # Modèle Fournisseur
│   └── ...            # Autres modèles
├── scripts/            # Scripts utilitaires
│   ├── migrations/    # Scripts de migration
│   ├── backup/        # Scripts de sauvegarde
│   └── maintenance/   # Scripts de maintenance
├── utils/             # Utilitaires
│   ├── validators.py  # Validateurs
│   └── helpers.py     # Fonctions helpers
└── tests/             # Tests unitaires et d'intégration
```

## Spécifications Techniques

### Configuration Base de Données
```python
# database.py
SQLALCHEMY_DATABASE_URL = "sqlite:///./verres.db"
POOL_SIZE = 20
MAX_OVERFLOW = 10
POOL_TIMEOUT = 30
POOL_RECYCLE = 3600
```

### Modèles de Données

#### Verre
```python
class Verre(Base):
    __tablename__ = "verres"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    variante = Column(String(50))
    hauteur_min = Column(Integer)
    hauteur_max = Column(Integer)
    indice = Column(Float, nullable=False)
    url_gravure = Column(String(255))
    url_source = Column(String(255))
    
    # Relations
    fournisseur_id = Column(Integer, ForeignKey("fournisseurs.id"))
    materiau_id = Column(Integer, ForeignKey("materiaux.id"))
    gamme_id = Column(Integer, ForeignKey("gammes.id"))
    serie_id = Column(Integer, ForeignKey("series.id"))
    
    # Indexes
    __table_args__ = (
        Index('idx_verre_nom', 'nom'),
        Index('idx_verre_indice', 'indice'),
    )
```

#### Fournisseur
```python
class Fournisseur(Base):
    __tablename__ = "fournisseurs"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    verres = relationship("Verre", back_populates="fournisseur")
```

[... autres modèles ...]

## Performance

### Optimisations
1. Indexes stratégiques
   - Clés primaires (B-tree)
   - Clés étrangères
   - Colonnes fréquemment recherchées

2. Configuration Pool
   - Pool_size: 20 connexions
   - Max_overflow: 10 connexions
   - Pool_timeout: 30 secondes

3. Requêtes optimisées
   - Lazy loading
   - Jointures efficaces
   - Pagination

### Métriques
- Temps de requête moyen: <50ms
- Temps de transaction: <100ms
- Taille DB max: 10GB
- Connexions simultanées: 100

## Sécurité

### Protection des Données
```python
# Validation des entrées
class VerreValidator:
    @staticmethod
    def validate_indice(indice: float) -> bool:
        return 1.0 <= indice <= 2.0

    @staticmethod
    def validate_hauteur(min: int, max: int) -> bool:
        return 0 <= min <= max <= 100
```

### Transactions
```python
# Gestion des transactions
def create_verre(db: Session, verre: VerreCreate):
    try:
        with db.begin_nested():
            db_verre = Verre(**verre.dict())
            db.add(db_verre)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise DBOperationError(str(e))
```

### Backup
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d)
sqlite3 verres.db ".backup '/backup/verres_$DATE.db'"
gzip "/backup/verres_$DATE.db"
```

## Migrations

### Alembic Configuration
```python
# alembic.ini
[alembic]
script_location = migrations
sqlalchemy.url = sqlite:///./verres.db
```

### Exemple Migration
```python
# versions/001_initial.py
def upgrade():
    op.create_table(
        'verres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(100), nullable=False),
        # ...
    )

def downgrade():
    op.drop_table('verres')
```

## Tests

### Tests Unitaires
```python
# test_models.py
def test_create_verre(db_session):
    verre = Verre(
        nom="Test",
        indice=1.5,
        fournisseur_id=1
    )
    db_session.add(verre)
    db_session.commit()
    assert verre.id is not None
```

### Tests d'Intégration
```python
# test_crud.py
def test_verre_crud():
    # Create
    verre = create_verre(db, verre_data)
    assert verre.id is not None
    
    # Read
    db_verre = get_verre(db, verre.id)
    assert db_verre.nom == verre_data.nom
    
    # Update
    update_verre(db, verre.id, update_data)
    db_verre = get_verre(db, verre.id)
    assert db_verre.indice == update_data.indice
    
    # Delete
    delete_verre(db, verre.id)
    assert get_verre(db, verre.id) is None
```

## Monitoring

### Métriques SQLAlchemy
```python
from sqlalchemy import event

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop()
    logger.info(f"Query took {total:.2f}s: {statement}")
```

### Logging
```python
# Configuration logging
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'database.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'sqlalchemy.engine': {
            'handlers': ['file'],
            'level': 'INFO',
        }
    }
}
```

## Maintenance

### Tâches Quotidiennes
1. Vérification des logs
2. Backup automatique
3. Monitoring des performances
4. Nettoyage des sessions

### Tâches Hebdomadaires
1. Analyse des requêtes lentes
2. Optimisation des indexes
3. Vérification intégrité
4. Compaction base

### Tâches Mensuelles
1. Revue des performances
2. Mise à jour schéma
3. Archivage données
4. Maintenance indexes

## Dépendances

### Requirements
```
sqlalchemy>=1.4.23
alembic>=1.7.1
psycopg2-binary>=2.9.1
mysqlclient>=2.0.3
python-dotenv>=0.19.0
```

### Compatibilité
- Python: 3.8+
- SQLite: 3.31+
- RAM: 4GB minimum
- Disk: SSD recommandé

## Troubleshooting

### Problèmes Courants
1. Connexions perdues
   - Vérifier pool_recycle
   - Augmenter timeout
   - Checker réseau

2. Performances dégradées
   - Analyser requêtes
   - Vérifier indexes
   - Optimiser jointures

3. Deadlocks
   - Réduire durée transactions
   - Ordonner opérations
   - Augmenter timeout

## Références

### Documentation
- SQLAlchemy Docs
- Alembic Docs
- SQLite Documentation
- Python DB-API 2.0

### Outils
- DB Browser for SQLite
- SQLAlchemy Debug Toolbar
- Alembic Revision Tool
- Database Profiler 