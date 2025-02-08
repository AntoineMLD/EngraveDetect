# api/routes/fournisseurs.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.dependencies.auth import verify_auth
from database.config.database import get_db
from database.models.base import Fournisseur


# Les modèles Pydantic pour la validation des données
class FournisseurBase(BaseModel):
    nom: str

    class Config:
        orm_mode = True

    @validator("nom")
    def validate_nom(cls, v):
        if not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        if len(v) > 255:
            raise ValueError("Le nom ne peut pas dépasser 255 caractères")
        return v.strip()


class FournisseurResponse(FournisseurBase):
    id: int


router = APIRouter()


# Routes GET (non protégées)
@router.get("/fournisseurs", response_model=List[FournisseurResponse])
def get_fournisseurs(db: Session = Depends(get_db)):
    try:
        fournisseurs = db.query(Fournisseur).all()
        return [FournisseurResponse.from_orm(f) for f in fournisseurs]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'accès à la base de données",
        )


# Obtenir un fournisseur par ID
@router.get("/fournisseurs/{fournisseur_id}", response_model=FournisseurResponse)
def get_fournisseur(fournisseur_id: int, db: Session = Depends(get_db)):
    try:
        fournisseur = (
            db.query(Fournisseur).filter(Fournisseur.id == fournisseur_id).first()
        )
        if fournisseur is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Fournisseur non trouvé"
            )
        return FournisseurResponse.from_orm(fournisseur)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'accès à la base de données",
        )


# Routes protégées (POST, PUT, DELETE)
@router.post(
    "/fournisseurs",
    response_model=FournisseurResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_fournisseur(
    fournisseur: FournisseurBase,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    try:
        db_fournisseur = Fournisseur(nom=fournisseur.nom)
        db.add(db_fournisseur)
        db.commit()
        db.refresh(db_fournisseur)
        return FournisseurResponse.from_orm(db_fournisseur)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du fournisseur: {str(e)}",
        )


@router.put("/fournisseurs/{fournisseur_id}", response_model=FournisseurResponse)
async def update_fournisseur(
    fournisseur_id: int,
    fournisseur: FournisseurBase,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    try:
        db_fournisseur = (
            db.query(Fournisseur).filter(Fournisseur.id == fournisseur_id).first()
        )
        if db_fournisseur is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Fournisseur non trouvé"
            )

        db_fournisseur.nom = fournisseur.nom
        db.commit()
        db.refresh(db_fournisseur)
        return FournisseurResponse.from_orm(db_fournisseur)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la modification du fournisseur: {str(e)}",
        )


@router.delete("/fournisseurs/{fournisseur_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fournisseur(
    fournisseur_id: int, db: Session = Depends(get_db), _: str = Depends(verify_auth)
):
    try:
        db_fournisseur = (
            db.query(Fournisseur).filter(Fournisseur.id == fournisseur_id).first()
        )
        if db_fournisseur is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Fournisseur non trouvé"
            )

        db.delete(db_fournisseur)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression du fournisseur: {str(e)}",
        )
