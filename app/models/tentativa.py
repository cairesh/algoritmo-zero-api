from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from app.database import Base


class Tentativa(Base):
    __tablename__ = "tentativas"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"), nullable=False, index=True)
    correto = Column(Boolean, nullable=False)
    data_hora = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
