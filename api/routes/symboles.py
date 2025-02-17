from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies.auth import verify_auth
from database.config.database import get_db
from database.models.base import SymboleTag
from pydantic import BaseModel

router = APIRouter()

# Schémas Pydantic
class SymboleBase(BaseModel):
    nom: str
    description: Optional[str] = None

class SymboleCreate(SymboleBase):
    pass

class SymboleUpdate(SymboleBase):
    pass

class Symbole(SymboleBase):
    id: int
    
    class Config:
        orm_mode = True

# Routes CRUD
@router.get("/symboles/", response_model=List[Symbole], tags=["Symboles"])
def get_symboles(
    skip: int = Query(0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, description="Nombre maximum d'éléments à retourner"),
    search: Optional[str] = Query(None, description="Terme de recherche pour le nom"),
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    """
    Récupère la liste des symboles avec pagination et recherche optionnelle.
    """
    query = db.query(SymboleTag)
    
    if search:
        query = query.filter(SymboleTag.nom.ilike(f"%{search}%"))
    
    return query.offset(skip).limit(limit).all()

@router.post("/symboles/", response_model=Symbole, tags=["Symboles"])
def create_symbole(
    symbole: SymboleCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    """
    Crée un nouveau symbole.
    """
    db_symbole = SymboleTag(**symbole.dict())
    db.add(db_symbole)
    
    try:
        db.commit()
        db.refresh(db_symbole)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de créer le symbole : {str(e)}",
        )
    
    return db_symbole

@router.get("/symboles/{symbole_id}", response_model=Symbole, tags=["Symboles"])
def get_symbole(
    symbole_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    """
    Récupère un symbole par son ID.
    """
    symbole = db.query(SymboleTag).filter(SymboleTag.id == symbole_id).first()
    if not symbole:
        raise HTTPException(status_code=404, detail="Symbole non trouvé")
    return symbole

@router.put("/symboles/{symbole_id}", response_model=Symbole, tags=["Symboles"])
def update_symbole(
    symbole_id: int,
    symbole: SymboleUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    """
    Met à jour un symbole existant.
    """
    db_symbole = db.query(SymboleTag).filter(SymboleTag.id == symbole_id).first()
    if not db_symbole:
        raise HTTPException(status_code=404, detail="Symbole non trouvé")
    
    for key, value in symbole.dict(exclude_unset=True).items():
        setattr(db_symbole, key, value)
    
    try:
        db.commit()
        db.refresh(db_symbole)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de mettre à jour le symbole : {str(e)}",
        )
    
    return db_symbole

@router.delete("/symboles/{symbole_id}", tags=["Symboles"])
def delete_symbole(
    symbole_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    """
    Supprime un symbole.
    """
    symbole = db.query(SymboleTag).filter(SymboleTag.id == symbole_id).first()
    if not symbole:
        raise HTTPException(status_code=404, detail="Symbole non trouvé")
    
    try:
        db.delete(symbole)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de supprimer le symbole : {str(e)}",
        )
    
    return {"message": "Symbole supprimé avec succès"} 