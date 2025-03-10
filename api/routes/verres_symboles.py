from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import and_
from sqlalchemy.orm import Session

from api.dependencies.auth import verify_auth
from database.config.database import get_db
from database.models.base import SymboleTag, Verre, VerreSymbole

router = APIRouter()


# Schémas Pydantic
class VerreSymboleBase(BaseModel):
    verre_id: int
    symbole_id: int
    score_confiance: float = Field(..., ge=0, le=1)
    est_valide: bool = False
    valide_par: Optional[str] = None

    class Config:
        orm_mode = True


class VerreSymboleCreate(VerreSymboleBase):
    pass


class VerreSymboleUpdate(BaseModel):
    est_valide: bool
    valide_par: str

    class Config:
        orm_mode = True


class VerreSymboleResponse(VerreSymboleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Routes
@router.post(
    "/verres/{verre_id}/symboles/",
    response_model=VerreSymboleResponse,
    tags=["Associations Verres-Symboles"],
)
def create_verre_symbole(
    verre_id: int,
    association: VerreSymboleCreate,
    db: Session = Depends(get_db),
    username: str = Depends(verify_auth),
):
    """
    Crée une nouvelle association entre un verre et un symbole.
    """
    # Vérifier que le verre existe
    verre = db.query(Verre).filter(Verre.id == verre_id).first()
    if not verre:
        raise HTTPException(status_code=404, detail="Verre non trouvé")

    # Vérifier que le symbole existe
    symbole = (
        db.query(SymboleTag).filter(SymboleTag.id == association.symbole_id).first()
    )
    if not symbole:
        raise HTTPException(status_code=404, detail="Symbole non trouvé")

    # Vérifier si l'association existe déjà
    existing = (
        db.query(VerreSymbole)
        .filter(
            and_(
                VerreSymbole.verre_id == verre_id,
                VerreSymbole.symbole_id == association.symbole_id,
            )
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Cette association existe déjà")

    # Créer l'association
    db_association = VerreSymbole(
        verre_id=verre_id,
        symbole_id=association.symbole_id,
        score_confiance=association.score_confiance,
        est_valide=association.est_valide,
        valide_par=username if association.est_valide else None,
    )

    db.add(db_association)

    try:
        db.commit()
        db.refresh(db_association)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail=f"Impossible de créer l'association : {str(e)}"
        )

    return VerreSymboleResponse.from_orm(db_association)


@router.get(
    "/verres/{verre_id}/symboles/",
    response_model=List[VerreSymboleResponse],
    tags=["Associations Verres-Symboles"],
)
def get_symboles_for_verre(
    verre_id: int,
    skip: int = Query(0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, description="Nombre maximum d'éléments à retourner"),
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    """
    Récupère tous les symboles associés à un verre.
    """
    # Vérifier que le verre existe
    verre = db.query(Verre).filter(Verre.id == verre_id).first()
    if not verre:
        raise HTTPException(status_code=404, detail="Verre non trouvé")

    associations = (
        db.query(VerreSymbole)
        .filter(VerreSymbole.verre_id == verre_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [VerreSymboleResponse.from_orm(a) for a in associations]


@router.put(
    "/verres/{verre_id}/symboles/{symbole_id}",
    response_model=VerreSymboleResponse,
    tags=["Associations Verres-Symboles"],
)
def validate_verre_symbole(
    verre_id: int,
    symbole_id: int,
    update: VerreSymboleUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    """
    Valide ou invalide une association verre-symbole.
    """
    association = (
        db.query(VerreSymbole)
        .filter(
            and_(
                VerreSymbole.verre_id == verre_id, VerreSymbole.symbole_id == symbole_id
            )
        )
        .first()
    )

    if not association:
        raise HTTPException(status_code=404, detail="Association non trouvée")

    association.est_valide = update.est_valide
    association.valide_par = update.valide_par if update.est_valide else None
    association.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(association)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Impossible de mettre à jour l'association : {str(e)}",
        )

    return VerreSymboleResponse.from_orm(association)


@router.delete(
    "/verres/{verre_id}/symboles/{symbole_id}", tags=["Associations Verres-Symboles"]
)
def delete_verre_symbole(
    verre_id: int,
    symbole_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_auth),
):
    """
    Supprime une association verre-symbole.
    """
    association = (
        db.query(VerreSymbole)
        .filter(
            and_(
                VerreSymbole.verre_id == verre_id, VerreSymbole.symbole_id == symbole_id
            )
        )
        .first()
    )

    if not association:
        raise HTTPException(status_code=404, detail="Association non trouvée")

    try:
        db.delete(association)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail=f"Impossible de supprimer l'association : {str(e)}"
        )

    return {"message": "Association supprimée avec succès"}
