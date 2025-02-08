import logging
import re
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from bs4 import BeautifulSoup


class NettoyeurDonneesOptiques:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Valeurs par défaut pour toutes les colonnes
        self.VALEURS_DEFAUT = {
            "nom_du_verre": "INCONNU",
            "gamme": "STANDARD",
            "serie": "INCONNU",
            "variante": "STANDARD",
            "hauteur_min": 14,  # Hauteur minimale standard
            "hauteur_max": 14,  # Hauteur maximale standard
            "traitement_protection": "NON",
            "traitement_photochromique": "NON",
            "materiau": "ORGANIQUE",
            "indice": 1.5,
            "fournisseur": "INCONNU",
            "url_gravure": "",
            "url_source": "",
        }

        # Mappings spécifiques pour Essilor
        self.MAPPING_MATERIAUX = {
            "ORG": "ORGANIQUE",
            "Orma": "ORGANIQUE_ORMA",
            "Ormix": "ORGANIQUE_ORMIX",
            "Stylis": "ORGANIQUE_STYLIS",
            "Airwear": "POLYCARBONATE_AIRWEAR",
            "Lineis": "ORGANIQUE_LINEIS",
        }

        self.MAPPING_GAMMES = {
            "Varilux": "PROGRESSIF_PREMIUM",
            "Eyezen": "UNIFOCAL_DIGITAL",
            "Essilor": "STANDARD",
        }

        self.SERIES_CONNUES = {
            "Comfort": {"type": "CONFORT", "niveau": "STANDARD"},
            "Physio": {"type": "PRECISION", "niveau": "PREMIUM"},
            "Liberty": {"type": "ECONOMIQUE", "niveau": "BASIQUE"},
            "XR": {"type": "INNOVATION", "niveau": "PREMIUM_PLUS"},
            "Digitime": {"type": "DIGITAL", "niveau": "SPECIALISE"},
        }

    def extraire_url_image(self, html_str: str) -> str:
        """Extrait l'URL de l'image depuis une balise HTML."""
        if pd.isna(html_str):
            return self.VALEURS_DEFAUT["url_gravure"]

        try:
            if "<img" in html_str:
                soup = BeautifulSoup(html_str, "html.parser")
                img_tag = soup.find("img")
                return img_tag["src"] if img_tag else self.VALEURS_DEFAUT["url_gravure"]
        except Exception as e:
            self.logger.warning(f"Erreur lors de l'extraction de l'URL: {str(e)}")
            return self.VALEURS_DEFAUT["url_gravure"]

        return html_str.strip()

    def nettoyer_gravure_text(self, url_image: str) -> str:
        """Nettoie la gravure textuelle."""
        if pd.isna(url_image):
            return self.VALEURS_DEFAUT["url_gravure"]

        return url_image.replace("<br/>", "").replace("CORRIDOR", "").strip()

    def nettoyer_materiau(self, materiau: str) -> str:
        """Nettoie et standardise le matériau."""
        if pd.isna(materiau):
            return self.VALEURS_DEFAUT["materiau"]

        try:
            # Nettoyage des balises HTML
            if "<" in materiau:
                materiau = BeautifulSoup(materiau, "html.parser").get_text().strip()

            # Application du mapping
            materiau_clean = materiau.strip()
            return self.MAPPING_MATERIAUX.get(
                materiau_clean, self.VALEURS_DEFAUT["materiau"]
            )

        except Exception as e:
            self.logger.warning(f"Erreur lors du nettoyage du matériau: {str(e)}")
            return self.VALEURS_DEFAUT["materiau"]

    def analyser_nom_verre(self, nom_verre: str) -> Dict[str, Any]:
        """Analyse détaillée du nom du verre."""
        if pd.isna(nom_verre):
            return {
                k: v
                for k, v in self.VALEURS_DEFAUT.items()
                if k
                in [
                    "nom_du_verre",
                    "gamme",
                    "serie",
                    "variante",
                    "hauteur_min",
                    "hauteur_max",
                    "traitement_protection",
                    "traitement_photochromique",
                ]
            }

        try:
            composants = nom_verre.split(" ")

            # Extraction de la nom_du_verre (premier mot)
            nom_du_verre = composants[0]
            gamme = self.MAPPING_GAMMES.get(nom_du_verre, self.VALEURS_DEFAUT["gamme"])

            # Recherche de la série
            serie = self.VALEURS_DEFAUT["serie"]
            for serie_connue in self.SERIES_CONNUES.keys():
                if serie_connue in nom_verre:
                    serie = serie_connue
                    break

            # Détection des traitements
            traitement_protection = (
                "OUI"
                if "Eye Protect System" or "Blue Natural" or "UVBlue" in nom_verre
                else "NON"
            )
            traitement_photochromique = (
                "OUI" if "Transitions" or "Trans®" in nom_verre else "NON"
            )

            # Détection des variantes
            variantes = []
            if "Short" in nom_verre:
                variantes.append("COURT")
            if "Fit" in nom_verre or "FIT" in nom_verre:
                variantes.append("ADAPTATIF")

            variante = (
                "|".join(variantes) if variantes else self.VALEURS_DEFAUT["variante"]
            )

            # Hauteurs par défaut selon la variante
            hauteur_min = 14
            hauteur_max = 14
            if "COURT" in variante:
                hauteur_min = 11
                hauteur_max = 11

            return {
                "nom_du_verre": nom_du_verre,
                "gamme": gamme,
                "serie": serie,
                "variante": variante,
                "hauteur_min": hauteur_min,
                "hauteur_max": hauteur_max,
                "traitement_protection": traitement_protection,
                "traitement_photochromique": traitement_photochromique,
            }

        except Exception as e:
            self.logger.warning(f"Erreur lors de l'analyse du nom: {str(e)}")
            return {
                k: v
                for k, v in self.VALEURS_DEFAUT.items()
                if k
                in [
                    "nom_du_verre",
                    "gamme",
                    "serie",
                    "variante",
                    "hauteur_min",
                    "hauteur_max",
                    "traitement_protection",
                    "traitement_photochromique",
                ]
            }

    def nettoyer_indice(self, indice_val: Any) -> list:
        """Nettoie et convertit l'indice en liste de floats. Gère les types non-string et les intervalles avec différents séparateurs."""
        if pd.isna(indice_val):
            return [self.VALEURS_DEFAUT["indice"]]

        if isinstance(indice_val, (int, float)):
            return [float(indice_val)]

        if not isinstance(indice_val, (str, bytes)):
            self.logger.warning(
                f"Type d'indice non géré : {type(indice_val)}, valeur: {indice_val}"
            )
            return [self.VALEURS_DEFAUT["indice"]]

        try:
            indice_str = str(indice_val)
            # Utilisation d'une expression régulière pour splitter avec plusieurs séparateurs
            parts = re.split(r"[/\s-]", indice_str)  # Split sur /, espace et -
            indices = []
            for part in parts:
                part = re.sub(r"[^\d.]", "", part).strip()
                if part:
                    try:
                        indices.append(float(part))
                    except ValueError:
                        self.logger.warning(
                            f"Valeur d'indice invalide : {part} dans la chaîne originale : {indice_val}"
                        )
                        return [self.VALEURS_DEFAUT["indice"]]
            if not indices:
                return [self.VALEURS_DEFAUT["indice"]]
            return indices
        except Exception as e:
            self.logger.warning(
                f"Erreur inattendue lors du nettoyage de l'indice : {e}"
            )
            return [self.VALEURS_DEFAUT["indice"]]

    def nettoyer_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie et enrichit le DataFrame complet."""
        df_propre = pd.DataFrame()

        try:
            # Traitement des noms de verre
            noms_traites = df["glass_name"].apply(self.analyser_nom_verre)

            # Attribution des colonnes analysées
            df_propre["nom_du_verre"] = noms_traites.apply(lambda x: x["nom_du_verre"])
            df_propre["gamme"] = noms_traites.apply(lambda x: x["gamme"])
            df_propre["serie"] = noms_traites.apply(lambda x: x["serie"])
            df_propre["variante"] = noms_traites.apply(lambda x: x["variante"])
            df_propre["hauteur_min"] = noms_traites.apply(lambda x: x["hauteur_min"])
            df_propre["hauteur_max"] = noms_traites.apply(lambda x: x["hauteur_max"])
            df_propre["traitement_protection"] = noms_traites.apply(
                lambda x: x["traitement_protection"]
            )
            df_propre["traitement_photochromique"] = noms_traites.apply(
                lambda x: x["traitement_photochromique"]
            )

            # Autres colonnes
            df_propre["materiau"] = df["material"].apply(self.nettoyer_materiau)
            df_propre["indices"] = df["glass_index"].apply(self.nettoyer_indice)
            # Duplication des lignes pour chaque indice
            df_propre = df_propre.explode("indices")
            df_propre = df_propre.rename(columns={"indices": "indice"})
            df_propre["fournisseur"] = df["glass_supplier_name"].fillna(
                self.VALEURS_DEFAUT["fournisseur"]
            )
            df_propre["url_gravure"] = df["nasal_engraving"].apply(
                self.extraire_url_image
            )
            df_propre["url_gravure"] = df_propre["url_gravure"].apply(
                self.nettoyer_gravure_text
            )
            df_propre["url_source"] = df["source_url"].fillna(
                self.VALEURS_DEFAUT["url_source"]
            )

            # Validation des données
            df_propre.loc[~df_propre["indice"].between(1.4, 1.9), "indice"] = (
                self.VALEURS_DEFAUT["indice"]
            )

            return df_propre

        except Exception as e:
            self.logger.error(f"Erreur lors du nettoyage du DataFrame: {str(e)}")
            raise

    def nettoyer_fichier(self, chemin_entree: Path, dossier_sortie: Path):
        """Traite un fichier CSV et sauvegarde le résultat nettoyé."""
        try:
            dossier_sortie.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Traitement du fichier: {chemin_entree.name}")

            df = pd.read_csv(chemin_entree)
            df_propre = self.nettoyer_dataframe(df)

            chemin_sortie = dossier_sortie / f"enhanced_{chemin_entree.name}"
            df_propre.to_csv(chemin_sortie, index=False)
            self.logger.info(f"Fichier nettoyé sauvegardé: {chemin_sortie}")

        except Exception as e:
            self.logger.error(
                f"Erreur lors du traitement de {chemin_entree.name}: {str(e)}"
            )
            raise


def main():
    nettoyeur = NettoyeurDonneesOptiques()

    racine_projet = Path(__file__).parent.parent.parent
    staging_folder = racine_projet / "scrapers" / "datalake" / "staging" / "data"
    enhanced_folder = racine_projet / "scrapers" / "datalake" / "enhanced" / "data"

    # Liste tous les fichiers CSV dans le dossier staging
    fichiers_entree = [
        x for x in staging_folder.iterdir() if x.is_file() and x.suffix == ".csv"
    ]

    print(f"Nombre de fichiers à traiter: {len(fichiers_entree)}")
    print("Fichiers à traiter:")
    for fichier in fichiers_entree:
        print(fichier)

    # Traitement de chaque fichier
    for chemin_fichier in fichiers_entree:
        try:
            print(f"\nTraitement du fichier: {chemin_fichier.name}")
            nettoyeur.nettoyer_fichier(chemin_fichier, enhanced_folder)
            print(f"Fichier traité avec succès: {chemin_fichier.name}")

        except Exception as e:
            print(f"Erreur lors du traitement de {chemin_fichier.name}: {str(e)}")


if __name__ == "__main__":
    main()
