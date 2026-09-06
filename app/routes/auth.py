from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
from app.security import criar_token, administrador, usuario_atual
from app.models.tentativa import Tentativa
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioLogin, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticacao"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/cadastro", response_model=UsuarioResponse)
def cadastrar(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Este e-mail ja esta cadastrado.")

    senha_hash = pwd_context.hash(usuario.senha)

    novo_usuario = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_hash,
        tipo="estudante"
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario

@router.post("/login")
def login(dados: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if not usuario or not pwd_context.verify(dados.senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")

    return {
        "access_token": criar_token(usuario.id),
        "token_type": "bearer",
        "mensagem": "Login realizado com sucesso!",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "tipo": usuario.tipo
        }
    }
@router.put("/usuarios/{usuario_id}/promover", response_model=UsuarioResponse, dependencies=[Depends(administrador)])
def promover_usuario(usuario_id: int, novo_tipo: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado.")

    if novo_tipo not in ["estudante", "professor", "administrador"]:
        raise HTTPException(status_code=400, detail="Tipo invalido.")

    if usuario.tipo == "administrador" and novo_tipo != "administrador" and db.query(Usuario).filter(Usuario.tipo == "administrador").count() <= 1:
        raise HTTPException(409, "Nao e possivel rebaixar o ultimo administrador.")

    usuario.tipo = novo_tipo
    db.commit()
    db.refresh(usuario)

    return usuario
@router.get("/usuarios", response_model=list[UsuarioResponse], dependencies=[Depends(administrador)])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

@router.get("/me", response_model=UsuarioResponse)
def me(usuario: Usuario = Depends(usuario_atual)):
    return usuario


@router.delete("/usuarios/{usuario_id}", status_code=204, dependencies=[Depends(administrador)])
def remover_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario nao encontrado.")
    if usuario.tipo == "administrador" and db.query(Usuario).filter(Usuario.tipo == "administrador").count() <= 1:
        raise HTTPException(409, "Nao e possivel remover o ultimo administrador.")
    db.query(Tentativa).filter(Tentativa.usuario_id == usuario_id).delete(synchronize_session=False)
    db.delete(usuario)
    db.commit()
