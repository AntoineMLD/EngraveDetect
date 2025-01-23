# api/routes/verres.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database.models.base import Verre, Traitement
from database.config.database import get_db
from api.dependencies.auth import verify_auth

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
@router.post("/verres", response_model=VerreResponse)
async def create_verre(
    verre: VerreBase,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_verre = Verre(**verre.dict())
    db.add(db_verre)
    db.commit()
    db.refresh(db_verre)
    return db_verre

@router.put("/verres/{verre_id}", response_model=VerreResponse)
async def update_verre(
    verre_id: int,
    verre: VerreBase,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_verre = db.query(Verre).filter(Verre.id == verre_id).first()
    if db_verre is None:
        raise HTTPException(status_code=404, detail="Verre non trouvé")
    
    for key, value in verre.dict(exclude_unset=True).items():
        setattr(db_verre, key, value)
    
    db.commit()
    db.refresh(db_verre)
    return db_verre

@router.delete("/verres/{verre_id}")
async def delete_verre(
    verre_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth)
):
    db_verre = db.query(Verre).filter(Verre.id == verre_id).first()
    if db_verre is None:
        raise HTTPException(status_code=404, detail="Verre non trouvé")
    
    db.delete(db_verre)
    db.commit()
    return {"message": "Verre supprimé"}

