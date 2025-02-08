# api/routes/verres.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.dependencies.auth import verify_auth
from database.config.database import get_db
from database.models.base import Traitement, Verre


# Modèle Pydantic pour les traitements
class TraitementResponse(BaseModel):
    id: int
    nom: str
    type: str

    class Config:
        orm_mode = True


class VerreBase(BaseModel):
    nom: Optional[str] = None
    variante: Optional[str] = None
    hauteur_min: Optional[int] = None
    hauteur_max: Optional[int] = None
    indice: Optional[float] = None
    url_gravure: Optional[str] = ""
    url_source: Optional[str] = None
    fournisseur_id: Optional[int] = None
    materiau_id: Optional[int] = None
    gamme_id: Optional[int] = None
    serie_id: Optional[int] = None

    class Config:
        orm_mode = True


class VerreResponse(VerreBase):
    id: int
    traitements: List[TraitementResponse] = []

    class Config:
        orm_mode = True


router = APIRouter()


# Routes GET (non protégées)
@router.get("/verres", response_model=List[VerreResponse])
async def get_verres(db: Session = Depends(get_db)):
    verres = db.query(Verre).all()
    return verres


@router.get("/verre/{verre_id}", response_model=VerreResponse)
async def get_verre(verre_id: int, db: Session = Depends(get_db)):
    verre = db.query(Verre).filter(Verre.id == verre_id).first()
    if verre is None:
        raise HTTPException(status_code=404, detail="Verre non trouvé")
    return verre


# Routes protégées (POST, PUT, DELETE)
@router.post(
    "/verres", response_model=VerreResponse, status_code=status.HTTP_201_CREATED
)
async def create_verre(
    verre: VerreBase, db: Session = Depends(get_db), _: str = Depends(verify_auth)
):
    try:
        db_verre = Verre(**verre.dict())
        db.add(db_verre)
        db.commit()
        db.refresh(db_verre)
        return db_verre
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du verre: {str(e)}",
        )


@router.put("/verres/{verre_id}", response_model=VerreResponse)
async def update_verre(
    verre_id: int,
    verre: VerreBase,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    try:
        db_verre = db.query(Verre).filter(Verre.id == verre_id).first()
        if db_verre is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Verre non trouvé"
            )

        for key, value in verre.dict(exclude_unset=True).items():
            setattr(db_verre, key, value)

        db.commit()
        db.refresh(db_verre)
        return db_verre
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour du verre: {str(e)}",
        )


@router.delete("/verres/{verre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_verre(
    verre_id: int, db: Session = Depends(get_db), _: str = Depends(verify_auth)
):
    try:
        db_verre = db.query(Verre).filter(Verre.id == verre_id).first()
        if db_verre is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Verre non trouvé"
            )

        db.delete(db_verre)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression du verre: {str(e)}",
        )
