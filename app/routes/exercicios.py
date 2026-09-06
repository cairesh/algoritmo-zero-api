from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.exercicio import Exercicio
from app.models.modulo import Modulo
from app.models.usuario import Usuario
from app.models.tentativa import Tentativa
from app.schemas.exercicio import ExercicioCreate, ExercicioResponse, ExercicioEdicaoResponse, VerificarResposta
from app.security import usuario_atual, equipe

router = APIRouter(prefix="/exercicios", tags=["Exercicios"])


def modulo_visivel(modulo_id, atual, db):
    modulo = db.get(Modulo, modulo_id)
    if not modulo or (atual.tipo == "estudante" and not modulo.publicado):
        raise HTTPException(404, "Modulo nao encontrado.")
    return modulo


@router.get("/modulo/{modulo_id}", response_model=list[ExercicioResponse])
def listar(modulo_id: int, db: Session = Depends(get_db), atual: Usuario = Depends(usuario_atual)):
    modulo_visivel(modulo_id, atual, db)
    return db.query(Exercicio).filter(Exercicio.modulo_id == modulo_id).order_by(Exercicio.ordem, Exercicio.id).all()


@router.get("/{exercicio_id}", response_model=ExercicioEdicaoResponse, dependencies=[Depends(equipe)])
def obter_para_edicao(exercicio_id: int, db: Session = Depends(get_db)):
    exercicio = db.get(Exercicio, exercicio_id)
    if not exercicio:
        raise HTTPException(404, "Exercicio nao encontrado.")
    return exercicio


@router.post("/", response_model=ExercicioEdicaoResponse, status_code=201)
def criar(exercicio: ExercicioCreate, db: Session = Depends(get_db), atual: Usuario = Depends(equipe)):
    modulo_visivel(exercicio.modulo_id, atual, db)
    novo = Exercicio(**exercicio.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{exercicio_id}", response_model=ExercicioEdicaoResponse)
def editar(exercicio_id: int, dados: ExercicioCreate, db: Session = Depends(get_db), atual: Usuario = Depends(equipe)):
    exercicio = db.get(Exercicio, exercicio_id)
    if not exercicio:
        raise HTTPException(404, "Exercicio nao encontrado.")
    modulo_visivel(dados.modulo_id, atual, db)
    for campo, valor in dados.model_dump().items():
        setattr(exercicio, campo, valor)
    db.commit()
    db.refresh(exercicio)
    return exercicio


@router.post("/{exercicio_id}/verificar")
def verificar(exercicio_id: int, dados: VerificarResposta, db: Session = Depends(get_db), atual: Usuario = Depends(usuario_atual)):
    exercicio = db.get(Exercicio, exercicio_id)
    if not exercicio:
        raise HTTPException(404, "Exercicio nao encontrado.")
    modulo_visivel(exercicio.modulo_id, atual, db)
    correto = dados.resposta.strip().casefold() == exercicio.gabarito.strip().casefold()
    if atual.tipo == "estudante":
        db.add(Tentativa(usuario_id=atual.id, exercicio_id=exercicio.id, correto=correto))
        db.commit()
    return {"correto": correto, "dica": exercicio.dica if not correto else None}
