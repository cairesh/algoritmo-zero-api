from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    tipo: Optional[str] = "estudante"

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    tipo: str

    class Config:
        from_attributes = True