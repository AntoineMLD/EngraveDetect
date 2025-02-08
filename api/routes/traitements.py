# api/routes/traitements.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.dependencies.auth import verify_auth
from database.config.database import get_db
from database.models.base import Traitement


class TraitementBase(BaseModel):
    nom: str
    type: str

    @validator("nom")
    def nom_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        return v.strip()

    @validator("type")
    def type_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Le type ne peut pas être vide")
        return v.strip()

    class Config:
        orm_mode = True


class TraitementResponse(TraitementBase):
    id: int


router = APIRouter()


# Routes GET (non protégées)
@router.get("/traitements", response_model=List[TraitementResponse])
def get_traitements(db: Session = Depends(get_db)):
    try:
        traitements = db.query(Traitement).all()
        return [
            TraitementResponse(id=t.id, nom=t.nom, type=t.type) for t in traitements
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des traitements: {str(e)}",
        )


@router.get("/traitements/{traitement_id}", response_model=TraitementResponse)
def get_traitement(traitement_id: int, db: Session = Depends(get_db)):
    try:
        traitement = db.query(Traitement).filter(Traitement.id == traitement_id).first()
        if traitement is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Traitement non trouvé"
            )
        return TraitementResponse(
            id=traitement.id, nom=traitement.nom, type=traitement.type
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du traitement: {str(e)}",
        )


# Routes protégées (POST, PUT, DELETE)
@router.post(
    "/traitements",
    response_model=TraitementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_traitement(
    traitement: TraitementBase,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    try:
        db_traitement = Traitement(nom=traitement.nom, type=traitement.type)
        db.add(db_traitement)
        db.commit()
        db.refresh(db_traitement)
        return TraitementResponse(
            id=db_traitement.id, nom=db_traitement.nom, type=db_traitement.type
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du traitement: {str(e)}",
        )


@router.put("/traitements/{traitement_id}", response_model=TraitementResponse)
async def update_traitement(
    traitement_id: int,
    traitement: TraitementBase,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    try:
        db_traitement = (
            db.query(Traitement).filter(Traitement.id == traitement_id).first()
        )
        if db_traitement is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Traitement non trouvé"
            )

        db_traitement.nom = traitement.nom
        db_traitement.type = traitement.type
        db.commit()
        db.refresh(db_traitement)
        return TraitementResponse(
            id=db_traitement.id, nom=db_traitement.nom, type=db_traitement.type
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour du traitement: {str(e)}",
        )


@router.delete("/traitements/{traitement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_traitement(
    traitement_id: int, db: Session = Depends(get_db), _: str = Depends(verify_auth)
):
    try:
        db_traitement = (
            db.query(Traitement).filter(Traitement.id == traitement_id).first()
        )
        if db_traitement is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Traitement non trouvé"
            )

        db.delete(db_traitement)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression du traitement: {str(e)}",
        )
