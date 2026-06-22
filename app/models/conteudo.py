from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Conteudo(Base):
    __tablename__ = "conteudos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    texto = Column(Text, nullable=False)
    ordem = Column(Integer, default=0)
    modulo_id = Column(Integer, ForeignKey("modulos.id"), nullable=False)

    modulo = relationship("Modulo", back_populates="conteudos")