from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.models.modulo import Modulo
from app.models.exercicio import Exercicio
from app.models.tentativa import Tentativa
from app.security import usuario_atual, equipe

router = APIRouter(prefix="/desempenho", tags=["Desempenho"])


def estatisticas(db, usuarios):
    ids = [u.id for u in usuarios]
    modulos = db.query(Modulo.id).filter(Modulo.publicado == 1).all()
    por_modulo = {m.id: set() for m in modulos}
    for e in db.query(Exercicio).join(Modulo).filter(Modulo.publicado == 1).all():
        por_modulo[e.modulo_id].add(e.id)
    tentativas = {uid: [] for uid in ids}
    if ids:
        for t in db.query(Tentativa).filter(Tentativa.usuario_id.in_(ids)).all():
            tentativas[t.usuario_id].append(t)
    resultado = []
    for u in usuarios:
        ts = tentativas[u.id]
        acertos = sum(t.correto for t in ts)
        resolvidos = {t.exercicio_id for t in ts if t.correto}
        concluidos = [mid for mid, exs in por_modulo.items() if exs and exs <= resolvidos]
        resultado.append({"usuario_id": u.id, "nome": u.nome, "email": u.email,
                          "total_tentativas": len(ts), "acertos": acertos,
                          "exercicios_feitos": len({t.exercicio_id for t in ts}),
                          "taxa_acerto": round(acertos * 100 / len(ts), 1) if ts else 0,
                          "modulos_concluidos": len(concluidos), "total_modulos": len(modulos),
                          "modulos_concluidos_ids": concluidos})
    return resultado


@router.get("/professor", dependencies=[Depends(equipe)])
def desempenho_professor(db: Session = Depends(get_db)):
    return estatisticas(db, db.query(Usuario).filter(Usuario.tipo == "estudante").order_by(Usuario.nome).all())


@router.get("/{usuario_id}")
def desempenho_usuario(usuario_id: int, atual: Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
    if atual.id != usuario_id and atual.tipo not in ("professor", "administrador"):
        raise HTTPException(403, "Voce so pode consultar seu proprio desempenho.")
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario nao encontrado.")
    return estatisticas(db, [usuario])[0]
