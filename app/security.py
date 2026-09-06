import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "")
if len(SECRET_KEY.encode()) < 32:
    raise RuntimeError("Defina JWT_SECRET_KEY com pelo menos 32 bytes aleatorios.")
TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
if TOKEN_MINUTES <= 0:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES deve ser positivo.")
bearer = HTTPBearer(auto_error=False)


def criar_token(usuario_id: int):
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(usuario_id), "iat": now,
                       "exp": now + timedelta(minutes=TOKEN_MINUTES)}, SECRET_KEY, algorithm="HS256")


def usuario_atual(credentials: HTTPAuthorizationCredentials = Depends(bearer),
                  db: Session = Depends(get_db)):
    erro = HTTPException(401, "Sessao invalida ou expirada.", headers={"WWW-Authenticate": "Bearer"})
    if credentials is None:
        raise erro
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"],
                             options={"require": ["sub", "exp", "iat"]})
        usuario_id = int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise erro
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise erro
    return usuario


def exigir_tipo(*tipos):
    def verificar(usuario: Usuario = Depends(usuario_atual)):
        if usuario.tipo not in tipos:
            raise HTTPException(403, "Voce nao tem permissao para esta operacao.")
        return usuario
    return verificar


equipe = exigir_tipo("professor", "administrador")
administrador = exigir_tipo("administrador")
