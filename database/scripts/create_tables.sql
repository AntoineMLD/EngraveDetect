-- Création des tables
CREATE TABLE IF NOT EXISTS fournisseurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS materiaux (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gammes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL UNIQUE,
    fournisseur_id INTEGER REFERENCES fournisseurs(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    gamme_id INTEGER REFERENCES gammes(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS traitements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100),
    variante VARCHAR(50),
    hauteur_min INTEGER,
    hauteur_max INTEGER,
    indice FLOAT NOT NULL,
    url_gravure VARCHAR(255),
    url_source VARCHAR(255),
    fournisseur_id INTEGER REFERENCES fournisseurs(id),
    materiau_id INTEGER REFERENCES materiaux(id),
    gamme_id INTEGER REFERENCES gammes(id),
    serie_id INTEGER REFERENCES series(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Création des index
CREATE INDEX IF NOT EXISTS idx_verres_nom ON verres(nom);
CREATE INDEX IF NOT EXISTS idx_verres_indice ON verres(indice);
CREATE INDEX IF NOT EXISTS idx_fournisseurs_nom ON fournisseurs(nom);
CREATE INDEX IF NOT EXISTS idx_materiaux_nom ON materiaux(nom);
CREATE INDEX IF NOT EXISTS idx_gammes_nom ON gammes(nom);
CREATE INDEX IF NOT EXISTS idx_series_nom ON series(nom);

-- Création des triggers pour updated_at
CREATE TRIGGER IF NOT EXISTS update_verres_updated_at
AFTER UPDATE ON verres
BEGIN
    UPDATE verres SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_fournisseurs_updated_at
AFTER UPDATE ON fournisseurs
BEGIN
    UPDATE fournisseurs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_materiaux_updated_at
AFTER UPDATE ON materiaux
BEGIN
    UPDATE materiaux SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_gammes_updated_at
AFTER UPDATE ON gammes
BEGIN
    UPDATE gammes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_series_updated_at
AFTER UPDATE ON series
BEGIN
    UPDATE series SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_traitements_updated_at
AFTER UPDATE ON traitements
BEGIN
    UPDATE traitements SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END; 