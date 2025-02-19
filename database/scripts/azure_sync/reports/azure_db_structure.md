# Structure de la base de données Azure SQL

## Table: dbo.gravures
Type: BASE TABLE
Nombre de colonnes: 6

### Colonnes:

| name            | type     |   max_length | nullable   | default     |
|:----------------|:---------|-------------:|:-----------|:------------|
| id              | int      |          nan | NO         |             |
| verre_id        | int      |          nan | YES        |             |
| type_gravure    | varchar  |           10 | YES        |             |
| contenu_textuel | varchar  |          255 | YES        |             |
| image_url       | varchar  |          500 | YES        |             |
| date_ajout      | datetime |          nan | YES        | (getdate()) |

---

## Table: dbo.symboles
Type: BASE TABLE
Nombre de colonnes: 3

### Colonnes:

| name   | type    |   max_length | nullable   | default   |
|:-------|:--------|-------------:|:-----------|:----------|
| id     | int     |          nan | NO         |           |
| nom    | varchar |          100 | NO         |           |
| type   | varchar |           50 | YES        |           |

---

## Table: dbo.verres
Type: BASE TABLE
Nombre de colonnes: 4

### Colonnes:

| name        | type    |    max_length | nullable   | default   |
|:------------|:--------|--------------:|:-----------|:----------|
| id          | int     | nan           | NO         |           |
| nom         | varchar | 255           | NO         |           |
| description | text    |   2.14748e+09 | YES        |           |
| categorie   | varchar | 100           | YES        |           |

---

## Table: dbo.verres_symboles
Type: BASE TABLE
Nombre de colonnes: 5

### Colonnes:

| name            | type   | max_length   | nullable   | default   |
|:----------------|:-------|:-------------|:-----------|:----------|
| id              | int    |              | NO         |           |
| verre_id        | int    |              | YES        |           |
| symbole_id      | int    |              | YES        |           |
| score_confiance | float  |              | YES        |           |
| est_valide      | bit    |              | YES        | ((0))     |

---

## Table: sys.database_firewall_rules
Type: VIEW
Nombre de colonnes: 6

### Colonnes:

| name             | type     |   max_length | nullable   | default   |
|:-----------------|:---------|-------------:|:-----------|:----------|
| id               | int      |          nan | NO         |           |
| name             | nvarchar |          128 | NO         |           |
| start_ip_address | varchar  |           45 | NO         |           |
| end_ip_address   | varchar  |           45 | NO         |           |
| create_date      | datetime |          nan | NO         |           |
| modify_date      | datetime |          nan | NO         |           |

---

