# api/routes/gammes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.models.base import Gamme
from database.config.database import get_db
from api.dependencies.auth import verify_auth


class GammeBase(BaseModel):
    nom: str 

    class Config:
        orm_mode = True 

router = APIRouter()

# Routes GET (non protégées)
@router.get("/gammes", response_model=List[GammeBase])
def get_gammes(db: Session = Depends(get_db)):
    return db.query(Gamme).all()

@router.get("/gammes/{gamme_id}", response_model=GammeBase)
def get_gamme(gamme_id: int, db: Session = Depends(get_db)):
    gamme = db.query(Gamme).filter(Gamme.id == gamme_id).first()
    if gamme is None:
        raise HTTPException(status_code=404, detail="Gamme non trouvée")
    return gamme

# Routes protégées (POST, PUT, DELETE)
@router.post("/gammes", response_model=GammeBase)
async def create_gamme(
    gamme: GammeBase, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_gamme = Gamme(nom=gamme.nom)
    db.add(db_gamme)
    db.commit()
    db.refresh(db_gamme)
    return db_gamme

@router.put("/gammes/{gamme_id}", response_model=GammeBase)
async def update_gamme(
    gamme_id: int, 
    gamme: GammeBase, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_gamme = db.query(Gamme).filter(Gamme.id == gamme_id).first()
    if db_gamme is None:
        raise HTTPException(status_code=404, detail="Gamme non trouvée")
    
    db_gamme.nom = gamme.nom
    db.commit()
    db.refresh(db_gamme)
    return db_gamme

@router.delete("/gammes/{gamme_id}")
async def delete_gamme(
    gamme_id: int, 
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_gamme = db.query(Gamme).filter(Gamme.id == gamme_id).first()
    if db_gamme is None:
        raise HTTPException(status_code=404, detail="Gamme non trouvée")
    
    db.delete(db_gamme)
    db.commit()
    return {"message": "Gamme supprimée"}