from pydantic import BaseModel
from typing import Optional

class ExercicioCreate(BaseModel):
    enunciado: str
    gabarito: str
    dica: Optional[str] = None
    ordem: Optional[int] = 0
    modulo_id: int

class ExercicioResponse(BaseModel):
    id: int
    enunciado: str
    dica: Optional[str]
    ordem: int
    modulo_id: int

    class Config:
        from_attributes = True

class VerificarResposta(BaseModel):
    resposta: str