from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Modulo(Base):
    __tablename__ = "modulos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    icone = Column(String(10), default="📦")
    ordem = Column(Integer, default=0)
    publicado = Column(Integer, default=0)  # 0 = rascunho, 1 = publicado

    conteudos = relationship("Conteudo", back_populates="modulo")
    exercicios = relationship("Exercicio", back_populates="modulo")