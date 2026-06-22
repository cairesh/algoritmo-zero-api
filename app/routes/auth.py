from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import get_db
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
        "mensagem": "Login realizado com sucesso!",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "tipo": usuario.tipo
        }
    }
@router.put("/usuarios/{usuario_id}/promover")
def promover_usuario(usuario_id: int, novo_tipo: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado.")

    if novo_tipo not in ["estudante", "professor", "administrador"]:
        raise HTTPException(status_code=400, detail="Tipo invalido.")

    usuario.tipo = novo_tipo
    db.commit()
    db.refresh(usuario)

    return {"mensagem": f"Usuario promovido para {novo_tipo} com sucesso!", "usuario": usuario}
@router.get("/usuarios", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()