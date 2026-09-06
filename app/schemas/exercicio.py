from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExercicioCreate(BaseModel):
    enunciado: str = Field(min_length=1)
    gabarito: str = Field(min_length=1, max_length=255)
    dica: str | None = Field(default=None, max_length=255)
    ordem: int = Field(default=0, ge=0)
    modulo_id: int = Field(gt=0)

    @field_validator("enunciado", "gabarito")
    @classmethod
    def nao_vazio(cls, valor):
        if not valor.strip():
            raise ValueError("Campo obrigatorio.")
        return valor


class ExercicioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    enunciado: str
    dica: str | None
    ordem: int
    modulo_id: int


class ExercicioEdicaoResponse(ExercicioResponse):
    gabarito: str


class VerificarResposta(BaseModel):
    resposta: str = Field(min_length=1, max_length=255)

    @field_validator("resposta")
    @classmethod
    def nao_vazia(cls, valor):
        if not valor.strip():
            raise ValueError("Informe uma resposta.")
        return valor
