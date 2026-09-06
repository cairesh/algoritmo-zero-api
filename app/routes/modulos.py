from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import equipe, usuario_atual
from app.models.usuario import Usuario
from app.models.modulo import Modulo
from app.schemas.modulo import ModuloCreate, ModuloResponse
from typing import List

router = APIRouter(prefix="/modulos", tags=["Modulos"], dependencies=[Depends(usuario_atual)])

@router.get("/", response_model=List[ModuloResponse])
def listar_modulos(db: Session = Depends(get_db), atual: Usuario = Depends(usuario_atual)):
    query = db.query(Modulo)
    if atual.tipo == "estudante":
        query = query.filter(Modulo.publicado == 1)
    return query.order_by(Modulo.ordem).all()

@router.get("/{modulo_id}", response_model=ModuloResponse)
def obter_modulo(modulo_id: int, db: Session = Depends(get_db), atual: Usuario = Depends(usuario_atual)):
    modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not modulo or (atual.tipo == "estudante" and not modulo.publicado):
        raise HTTPException(status_code=404, detail="Modulo nao encontrado.")
    return modulo

@router.post("/", response_model=ModuloResponse, dependencies=[Depends(equipe)])
def criar_modulo(modulo: ModuloCreate, db: Session = Depends(get_db)):
    novo_modulo = Modulo(**modulo.model_dump())
    db.add(novo_modulo)
    db.commit()
    db.refresh(novo_modulo)
    return novo_modulo

@router.put("/{modulo_id}/publicar", dependencies=[Depends(equipe)])
def publicar_modulo(modulo_id: int, db: Session = Depends(get_db)):
    modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo nao encontrado.")
    modulo.publicado = 1
    db.commit()
    return {"mensagem": "Modulo publicado com sucesso!"}