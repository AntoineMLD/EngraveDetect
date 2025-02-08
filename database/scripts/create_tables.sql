-- Création des tables
CREATE TABLE IF NOT EXISTS fournisseurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS materiaux (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gammes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    fournisseur_id INTEGER REFERENCES fournisseurs(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS series (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    gamme_id INTEGER REFERENCES gammes(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS traitements (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verres (
    id SERIAL PRIMARY KEY,
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Création des index
CREATE INDEX IF NOT EXISTS idx_verres_nom ON verres(nom);
CREATE INDEX IF NOT EXISTS idx_verres_indice ON verres(indice);
CREATE INDEX IF NOT EXISTS idx_fournisseurs_nom ON fournisseurs(nom);
CREATE INDEX IF NOT EXISTS idx_materiaux_nom ON materiaux(nom);
CREATE INDEX IF NOT EXISTS idx_gammes_nom ON gammes(nom);
CREATE INDEX IF NOT EXISTS idx_series_nom ON series(nom);

-- Création des triggers pour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_verres_updated_at
    BEFORE UPDATE ON verres
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fournisseurs_updated_at
    BEFORE UPDATE ON fournisseurs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_materiaux_updated_at
    BEFORE UPDATE ON materiaux
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gammes_updated_at
    BEFORE UPDATE ON gammes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_series_updated_at
    BEFORE UPDATE ON series
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_traitements_updated_at
    BEFORE UPDATE ON traitements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 