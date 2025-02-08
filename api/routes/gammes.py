# api/routes/gammes.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.dependencies.auth import verify_auth
from database.config.database import get_db
from database.models.base import Gamme


class GammeBase(BaseModel):
    nom: str

    class Config:
        orm_mode = True


class GammeResponse(GammeBase):
    id: int

    class Config:
        orm_mode = True


router = APIRouter()


# Routes GET (non protégées)
@router.get("/gammes", response_model=List[GammeResponse])
def get_gammes(db: Session = Depends(get_db)):
    try:
        return db.query(Gamme).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'accès à la base de données",
        )


@router.get("/gammes/{gamme_id}", response_model=GammeResponse)
def get_gamme(gamme_id: int, db: Session = Depends(get_db)):
    try:
        gamme = db.query(Gamme).filter(Gamme.id == gamme_id).first()
        if gamme is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Gamme non trouvée"
            )
        return gamme
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'accès à la base de données",
        )


# Routes protégées (POST, PUT, DELETE)
@router.post(
    "/gammes", response_model=GammeResponse, status_code=status.HTTP_201_CREATED
)
async def create_gamme(
    gamme: GammeBase, db: Session = Depends(get_db), _: str = Depends(verify_auth)
):
    try:
        db_gamme = Gamme(**gamme.dict())
        db.add(db_gamme)
        db.commit()
        db.refresh(db_gamme)
        return db_gamme
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la gamme: {str(e)}",
        )


@router.put("/gammes/{gamme_id}", response_model=GammeResponse)
async def update_gamme(
    gamme_id: int,
    gamme: GammeBase,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    try:
        db_gamme = db.query(Gamme).filter(Gamme.id == gamme_id).first()
        if db_gamme is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Gamme non trouvée"
            )

        for key, value in gamme.dict().items():
            setattr(db_gamme, key, value)

        db.commit()
        db.refresh(db_gamme)
        return db_gamme
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour de la gamme: {str(e)}",
        )


@router.delete("/gammes/{gamme_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gamme(
    gamme_id: int, db: Session = Depends(get_db), _: str = Depends(verify_auth)
):
    try:
        db_gamme = db.query(Gamme).filter(Gamme.id == gamme_id).first()
        if db_gamme is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Gamme non trouvée"
            )

        db.delete(db_gamme)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression de la gamme: {str(e)}",
        )
