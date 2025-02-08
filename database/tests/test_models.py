import pytest
from sqlalchemy.exc import IntegrityError

from database.models.base import Fournisseur, Gamme, Materiau, Serie, Traitement, Verre


class TestFournisseur:
    def test_create_fournisseur(self, test_db_session):
        """Test la création d'un fournisseur"""
        fournisseur = Fournisseur(nom="Test Fournisseur")
        test_db_session.add(fournisseur)
        test_db_session.commit()

        assert fournisseur.id is not None
        assert fournisseur.nom == "Test Fournisseur"

    def test_create_fournisseur_nom_unique(self, test_db_session):
        """Test l'unicité du nom du fournisseur"""
        fournisseur1 = Fournisseur(nom="Test Fournisseur")
        test_db_session.add(fournisseur1)
        test_db_session.commit()

        fournisseur2 = Fournisseur(nom="Test Fournisseur")
        test_db_session.add(fournisseur2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()

    def test_create_fournisseur_nom_required(self, test_db_session):
        """Test que le nom est requis"""
        fournisseur = Fournisseur(nom=None)
        test_db_session.add(fournisseur)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()


class TestMateriau:
    def test_create_materiau(self, test_db_session):
        """Test la création d'un matériau"""
        materiau = Materiau(nom="Test Materiau")
        test_db_session.add(materiau)
        test_db_session.commit()

        assert materiau.id is not None
        assert materiau.nom == "Test Materiau"

    def test_create_materiau_nom_unique(self, test_db_session):
        """Test l'unicité du nom du matériau"""
        materiau1 = Materiau(nom="Test Materiau")
        test_db_session.add(materiau1)
        test_db_session.commit()

        materiau2 = Materiau(nom="Test Materiau")
        test_db_session.add(materiau2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()

    def test_create_materiau_nom_required(self, test_db_session):
        """Test que le nom est requis"""
        materiau = Materiau(nom=None)
        test_db_session.add(materiau)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()


class TestGamme:
    def test_create_gamme(self, test_db_session):
        """Test la création d'une gamme"""
        gamme = Gamme(nom="Test Gamme")
        test_db_session.add(gamme)
        test_db_session.commit()

        assert gamme.id is not None
        assert gamme.nom == "Test Gamme"

    def test_create_gamme_nom_unique(self, test_db_session):
        """Test l'unicité du nom de la gamme"""
        gamme1 = Gamme(nom="Test Gamme")
        test_db_session.add(gamme1)
        test_db_session.commit()

        gamme2 = Gamme(nom="Test Gamme")
        test_db_session.add(gamme2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()

    def test_create_gamme_nom_required(self, test_db_session):
        """Test que le nom est requis"""
        gamme = Gamme(nom=None)
        test_db_session.add(gamme)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()


class TestSerie:
    def test_create_serie(self, test_db_session):
        """Test la création d'une série"""
        serie = Serie(nom="Test Serie")
        test_db_session.add(serie)
        test_db_session.commit()

        assert serie.id is not None
        assert serie.nom == "Test Serie"

    def test_create_serie_nom_unique(self, test_db_session):
        """Test l'unicité du nom de la série"""
        serie1 = Serie(nom="Test Serie")
        test_db_session.add(serie1)
        test_db_session.commit()

        serie2 = Serie(nom="Test Serie")
        test_db_session.add(serie2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()

    def test_create_serie_nom_required(self, test_db_session):
        """Test que le nom est requis"""
        serie = Serie(nom=None)
        test_db_session.add(serie)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()


class TestTraitement:
    def test_create_traitement(self, test_db_session):
        """Test la création d'un traitement"""
        traitement = Traitement(nom="Test Traitement", type="protection")
        test_db_session.add(traitement)
        test_db_session.commit()

        assert traitement.id is not None
        assert traitement.nom == "Test Traitement"
        assert traitement.type == "protection"

    def test_create_traitement_nom_unique(self, test_db_session):
        """Test l'unicité du nom du traitement"""
        traitement1 = Traitement(nom="Test Traitement", type="protection")
        test_db_session.add(traitement1)
        test_db_session.commit()

        traitement2 = Traitement(nom="Test Traitement", type="protection")
        test_db_session.add(traitement2)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()

    def test_create_traitement_nom_required(self, test_db_session):
        """Test que le nom est requis"""
        traitement = Traitement(nom=None, type="protection")
        test_db_session.add(traitement)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()

    def test_create_traitement_type_required(self, test_db_session):
        """Test que le type est requis"""
        traitement = Traitement(nom="Test Traitement", type=None)
        test_db_session.add(traitement)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()


class TestVerre:
    def test_create_verre(self, test_db_session):
        """Test la création d'un verre avec relations"""
        # Création des objets liés
        fournisseur = Fournisseur(nom="Test Fournisseur")
        gamme = Gamme(nom="Test Gamme")
        materiau = Materiau(nom="Test Materiau")
        serie = Serie(nom="Test Serie")
        traitement = Traitement(nom="Test Traitement", type="protection")

        test_db_session.add_all([fournisseur, gamme, materiau, serie, traitement])
        test_db_session.commit()

        # Création du verre
        verre = Verre(
            nom="Test Verre",
            variante="Test Variante",
            hauteur_min=10,
            hauteur_max=20,
            indice=1.5,
            fournisseur_id=fournisseur.id,
            materiau_id=materiau.id,
            gamme_id=gamme.id,
            serie_id=serie.id,
        )
        verre.traitements.append(traitement)

        test_db_session.add(verre)
        test_db_session.commit()

        assert verre.id is not None
        assert verre.nom == "Test Verre"
        assert verre.fournisseur.nom == "Test Fournisseur"
        assert verre.materiau.nom == "Test Materiau"
        assert verre.gamme.nom == "Test Gamme"
        assert verre.serie.nom == "Test Serie"
        assert len(verre.traitements) == 1
        assert verre.traitements[0].nom == "Test Traitement"

    def test_create_verre_fournisseur_required(self, test_db_session):
        """Test que le fournisseur est requis"""
        gamme = Gamme(nom="Test Gamme")
        test_db_session.add(gamme)
        test_db_session.commit()

        verre = Verre(nom="Test Verre", gamme_id=gamme.id, fournisseur_id=None)
        test_db_session.add(verre)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()

    def test_create_verre_gamme_required(self, test_db_session):
        """Test que la gamme est requise"""
        fournisseur = Fournisseur(nom="Test Fournisseur")
        test_db_session.add(fournisseur)
        test_db_session.commit()

        verre = Verre(nom="Test Verre", fournisseur_id=fournisseur.id, gamme_id=None)
        test_db_session.add(verre)
        with pytest.raises(IntegrityError):
            test_db_session.commit()
        test_db_session.rollback()

    def test_delete_verre_cascade(self, test_db_session):
        """Test la suppression en cascade des relations"""
        # Création des objets
        fournisseur = Fournisseur(nom="Test Fournisseur")
        gamme = Gamme(nom="Test Gamme")
        traitement = Traitement(nom="Test Traitement", type="protection")

        test_db_session.add_all([fournisseur, gamme, traitement])
        test_db_session.commit()

        verre = Verre(
            nom="Test Verre", fournisseur_id=fournisseur.id, gamme_id=gamme.id
        )
        verre.traitements.append(traitement)

        test_db_session.add(verre)
        test_db_session.commit()

        # Suppression du verre
        test_db_session.delete(verre)
        test_db_session.commit()

        # Vérification que les objets liés existent toujours
        assert test_db_session.query(Fournisseur).count() == 1
        assert test_db_session.query(Gamme).count() == 1
        assert test_db_session.query(Traitement).count() == 1
