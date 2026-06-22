from pydantic import BaseModel
from typing import Optional

class ModuloCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    icone: Optional[str] = "📦"
    ordem: Optional[int] = 0

class ModuloResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    icone: str
    ordem: int
    publicado: int

    class Config:
        from_attributes = True