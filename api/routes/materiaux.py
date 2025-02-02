# api/routes/materiaux.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from pydantic import BaseModel
from database.models.base import Materiau
from database.config.database import get_db
from api.dependencies.auth import verify_auth


class MateriauBase(BaseModel):
    nom: str 

    class Config:
        orm_mode = True 

class MateriauResponse(MateriauBase):
    id: int

    class Config:
        orm_mode = True

router = APIRouter()

# Routes GET (non protégées)
@router.get("/materiaux", response_model=List[MateriauResponse])
def get_materiaux(db: Session = Depends(get_db)):
    try:
        return db.query(Materiau).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'accès à la base de données"
        )

@router.get("/materiaux/{materiau_id}", response_model=MateriauResponse)
def get_materiau(materiau_id: int, db: Session = Depends(get_db)):
    try:
        materiau = db.query(Materiau).filter(Materiau.id == materiau_id).first()
        if materiau is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materiau non trouvé"
            )
        return materiau
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'accès à la base de données"
        )

# Routes protégées (POST, PUT, DELETE)
@router.post("/materiaux", response_model=MateriauResponse, status_code=status.HTTP_201_CREATED)
async def create_materiau(
    materiau: MateriauBase,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    try:
        db_materiau = Materiau(**materiau.dict())
        db.add(db_materiau)
        db.commit()
        db.refresh(db_materiau)
        return db_materiau
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du materiau"
        )

@router.put("/materiaux/{materiau_id}", response_model=MateriauResponse)
async def update_materiau(
    materiau_id: int,
    materiau: MateriauBase,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    try:
        db_materiau = db.query(Materiau).filter(Materiau.id == materiau_id).first()
        if db_materiau is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materiau non trouvé"
            )
        
        for key, value in materiau.dict().items():
            setattr(db_materiau, key, value)
        
        db.commit()
        db.refresh(db_materiau)
        return db_materiau
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du materiau"
        )

@router.delete("/materiaux/{materiau_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_materiau(
    materiau_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    try:
        db_materiau = db.query(Materiau).filter(Materiau.id == materiau_id).first()
        if db_materiau is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materiau non trouvé"
            )
        
        db.delete(db_materiau)
        db.commit()
        return None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression du materiau"
        )