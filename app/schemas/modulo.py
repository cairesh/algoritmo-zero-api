from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional

class ModuloCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=150)
    descricao: Optional[str] = None
    icone: str = Field(default="📦", max_length=10)
    ordem: int = Field(default=0, ge=0)

    @field_validator("titulo")
    @classmethod
    def titulo_valido(cls, valor):
        if not valor.strip():
            raise ValueError("Informe um titulo.")
        return valor.strip()

class ModuloResponse(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str]
    icone: str
    ordem: int
    publicado: int

    model_config = ConfigDict(from_attributes=True)
