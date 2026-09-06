from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=150)
    senha: str = Field(min_length=8)

    @field_validator("senha")
    @classmethod
    def tamanho_bcrypt(cls, valor):
        if len(valor.encode("utf-8")) > 72:
            raise ValueError("Senha deve ter no maximo 72 bytes em UTF-8.")
        return valor

    @field_validator("nome")
    @classmethod
    def nome_valido(cls, valor):
        if not valor.strip():
            raise ValueError("Informe seu nome.")
        return valor.strip()


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1)

    @field_validator("senha")
    @classmethod
    def tamanho_bcrypt(cls, valor):
        if len(valor.encode("utf-8")) > 72:
            raise ValueError("Senha deve ter no maximo 72 bytes em UTF-8.")
        return valor


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    email: str
    tipo: str
