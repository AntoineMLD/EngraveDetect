# api/routes/series.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.models.base import Serie
from database.config.database import get_db
from api.dependencies.auth import verify_auth

class SerieBase(BaseModel):
    nom: str 

    class Config:
        orm_mode = True 

router = APIRouter()

# Routes GET (non protégées)
@router.get("/series", response_model=List[SerieBase])
def get_series(db: Session = Depends(get_db)):
    return db.query(Serie).all()

@router.get("/series/{serie_id}", response_model=SerieBase)
def get_serie(serie_id: int, db: Session = Depends(get_db)):
    serie = db.query(Serie).filter(Serie.id == serie_id).first()
    if serie is None:
        raise HTTPException(status_code=404, detail="Serie non trouvée")
    return serie

# Routes protégées (POST, PUT, DELETE)
@router.post("/series", response_model=SerieBase)
async def create_serie(
    serie: SerieBase, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_serie = Serie(nom=serie.nom)
    db.add(db_serie)
    db.commit()
    db.refresh(db_serie)
    return db_serie

@router.put("/series/{serie_id}", response_model=SerieBase)
async def update_serie(
    serie_id: int, 
    serie: SerieBase, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_serie = db.query(Serie).filter(Serie.id == serie_id).first()
    if db_serie is None:
        raise HTTPException(status_code=404, detail="Serie non trouvée")
    
    db_serie.nom = serie.nom
    db.commit()
    db.refresh(db_serie)
    return db_serie

@router.delete("/series/{serie_id}")
async def delete_serie(
    serie_id: int, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_serie = db.query(Serie).filter(Serie.id == serie_id).first()
    if db_serie is None:
        raise HTTPException(status_code=404, detail="Serie non trouvée")
    
    db.delete(db_serie)
    db.commit()
    return {"message": "Serie supprimée"}