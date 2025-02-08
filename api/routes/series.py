# api/routes/series.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.dependencies.auth import verify_auth
from database.config.database import get_db
from database.models.base import Serie


class SerieBase(BaseModel):
    nom: str

    class Config:
        orm_mode = True


class SerieResponse(SerieBase):
    id: int

    class Config:
        orm_mode = True


router = APIRouter()


# Routes GET (non protégées)
@router.get("/series", response_model=List[SerieResponse])
def get_series(db: Session = Depends(get_db)):
    try:
        return db.query(Serie).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'accès à la base de données",
        )


@router.get("/series/{serie_id}", response_model=SerieResponse)
def get_serie(serie_id: int, db: Session = Depends(get_db)):
    try:
        serie = db.query(Serie).filter(Serie.id == serie_id).first()
        if serie is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Serie non trouvée"
            )
        return serie
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'accès à la base de données",
        )


# Routes protégées (POST, PUT, DELETE)
@router.post(
    "/series", response_model=SerieResponse, status_code=status.HTTP_201_CREATED
)
async def create_serie(
    serie: SerieBase, db: Session = Depends(get_db), _: str = Depends(verify_auth)
):
    try:
        db_serie = Serie(**serie.dict())
        db.add(db_serie)
        db.commit()
        db.refresh(db_serie)
        return db_serie
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de la serie",
        )


@router.put("/series/{serie_id}", response_model=SerieResponse)
async def update_serie(
    serie_id: int,
    serie: SerieBase,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    try:
        db_serie = db.query(Serie).filter(Serie.id == serie_id).first()
        if db_serie is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Serie non trouvée"
            )

        for key, value in serie.dict().items():
            setattr(db_serie, key, value)

        db.commit()
        db.refresh(db_serie)
        return db_serie
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour de la serie",
        )


@router.delete("/series/{serie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_serie(
    serie_id: int, db: Session = Depends(get_db), _: str = Depends(verify_auth)
):
    try:
        db_serie = db.query(Serie).filter(Serie.id == serie_id).first()
        if db_serie is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Serie non trouvée"
            )

        db.delete(db_serie)
        db.commit()
        return None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de la serie",
        )
