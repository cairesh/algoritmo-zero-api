from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.modulo import Modulo
from app.schemas.modulo import ModuloCreate, ModuloResponse
from typing import List

router = APIRouter(prefix="/modulos", tags=["Modulos"])

@router.get("/", response_model=List[ModuloResponse])
def listar_modulos(db: Session = Depends(get_db)):
    return db.query(Modulo).filter(Modulo.publicado == 1).order_by(Modulo.ordem).all()

@router.get("/{modulo_id}", response_model=ModuloResponse)
def obter_modulo(modulo_id: int, db: Session = Depends(get_db)):
    modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo nao encontrado.")
    return modulo

@router.post("/", response_model=ModuloResponse)
def criar_modulo(modulo: ModuloCreate, db: Session = Depends(get_db)):
    novo_modulo = Modulo(**modulo.dict())
    db.add(novo_modulo)
    db.commit()
    db.refresh(novo_modulo)
    return novo_modulo

@router.put("/{modulo_id}/publicar")
def publicar_modulo(modulo_id: int, db: Session = Depends(get_db)):
    modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo nao encontrado.")
    modulo.publicado = 1
    db.commit()
    return {"mensagem": "Modulo publicado com sucesso!"}