from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.exercicio import Exercicio
from app.schemas.exercicio import ExercicioCreate, ExercicioResponse, VerificarResposta
from typing import List

router = APIRouter(prefix="/exercicios", tags=["Exercicios"])

@router.get("/modulo/{modulo_id}", response_model=List[ExercicioResponse])
def listar_exercicios_do_modulo(modulo_id: int, db: Session = Depends(get_db)):
    return db.query(Exercicio).filter(Exercicio.modulo_id == modulo_id).order_by(Exercicio.ordem).all()

@router.post("/", response_model=ExercicioResponse)
def criar_exercicio(exercicio: ExercicioCreate, db: Session = Depends(get_db)):
    novo_exercicio = Exercicio(**exercicio.dict())
    db.add(novo_exercicio)
    db.commit()
    db.refresh(novo_exercicio)
    return novo_exercicio

@router.post("/{exercicio_id}/verificar")
def verificar_resposta(exercicio_id: int, dados: VerificarResposta, db: Session = Depends(get_db)):
    exercicio = db.query(Exercicio).filter(Exercicio.id == exercicio_id).first()
    if not exercicio:
        raise HTTPException(status_code=404, detail="Exercicio nao encontrado.")

    resposta_normalizada = dados.resposta.strip().lower()
    gabarito_normalizado = exercicio.gabarito.strip().lower()

    acertou = resposta_normalizada == gabarito_normalizado

    return {
        "correto": acertou,
        "dica": exercicio.dica if not acertou else None
    }