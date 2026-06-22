from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models import usuario, modulo, conteudo, exercicio
from app.routes import auth, modulos, exercicios

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Algoritmo Zero API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(modulos.router)
app.include_router(exercicios.router)

@app.get("/")
def read_root():
    return {"mensagem": "API do Algoritmo Zero funcionando!"}