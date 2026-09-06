import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models import usuario, modulo, conteudo, exercicio, tentativa
from app.routes import auth, modulos, exercicios, desempenho

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Algoritmo Zero API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(modulos.router)
app.include_router(exercicios.router)
app.include_router(desempenho.router)

@app.get("/")
def read_root():
    return {"mensagem": "API do Algoritmo Zero funcionando!"}