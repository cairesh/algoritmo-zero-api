from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Exercicio(Base):
    __tablename__ = "exercicios"

    id = Column(Integer, primary_key=True, index=True)
    enunciado = Column(Text, nullable=False)
    gabarito = Column(String(255), nullable=False)
    dica = Column(String(255), nullable=True)
    ordem = Column(Integer, default=0)
    modulo_id = Column(Integer, ForeignKey("modulos.id"), nullable=False)

    modulo = relationship("Modulo", back_populates="exercicios")