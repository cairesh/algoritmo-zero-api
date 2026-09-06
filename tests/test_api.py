import os
from datetime import datetime, timedelta, timezone
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET_KEY"] = "test-only-key-012345678901234567890123456789"

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models.usuario import Usuario
from app.models.modulo import Modulo
from app.models.exercicio import Exercicio
from app.models.tentativa import Tentativa
from app.routes.auth import pwd_context
from app.security import criar_token, SECRET_KEY


@pytest.fixture
def ctx():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    senha_hash = pwd_context.hash("senha1234")
    db.add_all([Usuario(id=i, nome=tipo, email=f"u{i}@example.com", tipo=tipo, senha_hash=senha_hash)
                for i, tipo in [(1, "estudante"), (2, "estudante"), (3, "professor"), (4, "administrador")]])
    db.add_all([Modulo(id=1, titulo="Publicado", publicado=1), Modulo(id=2, titulo="Rascunho"), Modulo(id=3, titulo="Vazio", publicado=1)])
    db.flush()
    db.add_all([Exercicio(id=i, modulo_id=mid, enunciado="Pergunta", gabarito="Sim", dica="Dica", ordem=i)
                for i, mid in [(1, 1), (2, 1), (3, 2)]])
    db.commit()
    def override():
        yield db
    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    yield client, db
    client.close()
    app.dependency_overrides.clear()
    db.close()
    engine.dispose()


def h(uid):
    return {"Authorization": f"Bearer {criar_token(uid)}"}


def test_login_and_identity(ctx):
    c, _ = ctx
    response = c.post("/auth/login", json={"email": "u1@example.com", "senha": "senha1234"})
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "senha_hash" not in data["usuario"]
    assert c.get("/auth/me", headers={"Authorization": f"Bearer {data['access_token']}"}).json()["id"] == 1
    assert c.post("/auth/login", json={"email": "u1@example.com", "senha": "errada"}).status_code == 401


@pytest.mark.parametrize("token", ["invalid", jwt.encode({"sub": "1", "iat": datetime.now(timezone.utc), "exp": datetime.now(timezone.utc)-timedelta(minutes=1)}, SECRET_KEY, algorithm="HS256"), jwt.encode({"sub": "1", "iat": datetime.now(timezone.utc), "exp": datetime.now(timezone.utc)+timedelta(minutes=1)}, "different-key-012345678901234567890123456789", algorithm="HS256")])
def test_bad_tokens(ctx, token):
    assert ctx[0].get("/modulos/", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_access_matrix(ctx):
    c, _ = ctx
    for path in ["/modulos/", "/auth/usuarios", "/exercicios/modulo/1", "/desempenho/1"]:
        assert c.get(path).status_code == 401
    assert c.get("/auth/usuarios", headers=h(1)).status_code == 403
    assert c.get("/auth/usuarios", headers=h(3)).status_code == 403
    assert c.put("/auth/usuarios/2/promover?novo_tipo=administrador", headers=h(1)).status_code == 403
    assert c.delete("/auth/usuarios/2", headers=h(3)).status_code == 403
    assert c.post("/modulos/", headers=h(1), json={"titulo": "Nao"}).status_code == 403
    assert c.put("/modulos/2/publicar", headers=h(1)).status_code == 403
    assert c.get("/desempenho/2", headers=h(1)).status_code == 403
    assert c.get("/desempenho/professor", headers=h(1)).status_code == 403
    assert c.get("/exercicios/1", headers=h(1)).status_code == 403
    assert c.get("/modulos/2", headers=h(1)).status_code == 404
    assert c.get("/exercicios/modulo/2", headers=h(1)).status_code == 404
    assert c.post("/exercicios/3/verificar", headers=h(1), json={"resposta": "Sim"}).status_code == 404
    assert "gabarito" not in c.get("/exercicios/modulo/1", headers=h(1)).json()[0]


def test_statistics_and_attempt_ownership(ctx):
    c, db = ctx
    for eid, resposta in [(1, "nao"), (1, " SIM "), (1, "Sim"), (2, "Sim")]:
        assert c.post(f"/exercicios/{eid}/verificar", headers=h(1), json={"resposta": resposta, "usuario_id": 2}).status_code == 200
    stats = c.get("/desempenho/1", headers=h(1)).json()
    assert stats["total_tentativas"] == 4
    assert stats["exercicios_feitos"] == 2
    assert stats["taxa_acerto"] == 75
    assert stats["modulos_concluidos"] == 1
    assert stats["total_modulos"] == 2
    assert stats["modulos_concluidos_ids"] == [1]
    assert all(t.usuario_id == 1 and t.data_hora is not None for t in db.query(Tentativa).all())
    alunos = c.get("/desempenho/professor", headers=h(3)).json()
    assert len(alunos) == 2
    assert next(a for a in alunos if a["usuario_id"] == 2)["taxa_acerto"] == 0
    c.post("/exercicios/1/verificar", headers=h(3), json={"resposta": "Sim"})
    assert db.query(Tentativa).count() == 4


def test_incomplete_module(ctx):
    c, _ = ctx
    c.post("/exercicios/1/verificar", headers=h(1), json={"resposta": "Sim"})
    assert c.get("/desempenho/1", headers=h(1)).json()["modulos_concluidos"] == 0


def test_edit_exercise(ctx):
    c, _ = ctx
    dados = {"enunciado": "Editado", "gabarito": "Novo", "dica": "Ajuda", "ordem": 8, "modulo_id": 1}
    assert c.put("/exercicios/1", headers=h(1), json=dados).status_code == 403
    assert c.put("/exercicios/1", headers=h(3), json=dados).status_code == 200
    assert c.get("/exercicios/1", headers=h(3)).json()["gabarito"] == "Novo"
    assert c.post("/exercicios/1/verificar", headers=h(1), json={"resposta": "novo"}).json()["correto"] is True
    assert c.put("/exercicios/99", headers=h(3), json=dados).status_code == 404
    assert c.post("/exercicios/", headers=h(3), json={**dados, "modulo_id": 999}).status_code == 404
    assert c.put("/exercicios/1", headers=h(3), json={**dados, "gabarito": " "}).status_code == 422


def test_admin_and_current_role(ctx):
    c, _ = ctx
    old_token = h(2)
    assert c.put("/auth/usuarios/2/promover?novo_tipo=professor", headers=h(4)).status_code == 200
    assert c.get("/desempenho/professor", headers=old_token).status_code == 200
    assert c.put("/auth/usuarios/2/promover?novo_tipo=estudante", headers=h(4)).status_code == 200
    assert c.get("/desempenho/professor", headers=old_token).status_code == 403
    assert "senha_hash" not in c.get("/auth/usuarios", headers=h(4)).text
    assert c.delete("/auth/usuarios/4", headers=h(4)).status_code == 409
    assert c.put("/auth/usuarios/4/promover?novo_tipo=estudante", headers=h(4)).status_code == 409
    assert c.put("/auth/usuarios/2/promover?novo_tipo=invalido", headers=h(4)).status_code == 400


def test_delete_revokes_and_removes_attempts(ctx):
    c, db = ctx
    token = h(1)
    c.post("/exercicios/1/verificar", headers=token, json={"resposta": "Sim"})
    assert c.delete("/auth/usuarios/1", headers=h(4)).status_code == 204
    assert db.query(Tentativa).count() == 0
    assert c.get("/auth/me", headers=token).status_code == 401


def test_registration_cannot_promote(ctx):
    c, _ = ctx
    response = c.post("/auth/cadastro", json={"nome": "Aluno", "email": "new@example.com", "senha": "senha1234", "tipo": "administrador"})
    assert response.status_code == 200
    assert response.json()["tipo"] == "estudante"
    assert "senha_hash" not in response.text
    assert c.post("/auth/cadastro", json={"nome": "Aluno", "email": "long@example.com", "senha": "a"*73}).status_code == 422
