# Algoritmo Zero API

## Executar localmente

1. Instale Python 3.12 ou superior e as dependências: `python -m pip install -r requirements.txt`.
2. Copie `.env.example` para `.env`, preservando seu `DATABASE_URL` existente.
3. Gere uma chave com `python -c "import secrets; print(secrets.token_urlsafe(48))"` e configure `JWT_SECRET_KEY`. Não publique essa chave.
4. Execute `uvicorn app.main:app --reload`.

A inicialização cria tabelas ausentes, incluindo `tentativas`; não recria tabelas existentes nem converte seu esquema. Faça backup antes da primeira atualização em produção. Tentativas anteriores à implementação não podem ser reconstruídas. Datas são armazenadas em UTC.

## Autenticação e permissões

`POST /auth/login` recebe JSON `{ "email": "...", "senha": "..." }` e retorna `access_token`, `token_type: bearer` e `usuario`. Envie `Authorization: Bearer <token>`. `GET /auth/me` valida a sessão. O cadastro público sempre cria estudantes, independentemente do tipo enviado.

O JWT usa HS256 com expiração de 60 minutos por padrão (`ACCESS_TOKEN_EXPIRE_MINUTES`). Cada requisição consulta o usuário no banco, portanto exclusões e mudanças de perfil têm efeito imediato na API. Logout remove o token do navegador; não revoga cópias do token antes da expiração. Não há refresh token nesta versão.

| Operação | Permissão |
| --- | --- |
| Listar módulos publicados e exercícios, responder | Autenticado |
| Criar/publicar módulos, criar/editar exercícios, ler gabarito | Professor ou administrador |
| Listar/promover/remover usuários | Administrador |
| Consultar desempenho individual | Próprio usuário, professor ou administrador |
| Consultar `/desempenho/professor` | Professor ou administrador |

Estudantes não acessam rascunhos. A listagem de exercícios não retorna gabarito; `GET /exercicios/{id}` fornece o formulário completo somente à equipe. `PUT /exercicios/{id}` recebe `enunciado`, `gabarito`, `dica`, `ordem` e `modulo_id`.

Promoção: `PUT /auth/usuarios/{id}/promover?novo_tipo=professor` (ou `administrador`). Exclusão: `DELETE /auth/usuarios/{id}` remove também suas tentativas. A API impede remover/rebaixar o único administrador. Para configurar o primeiro administrador, cadastre a conta normalmente e execute no ambiente da API `python -m app.bootstrap_admin email@exemplo.com`; o comando só funciona se ainda não houver administrador.

## Desempenho

`POST /exercicios/{id}/verificar` registra cada resposta de estudante usando o usuário do token. Professores podem testar respostas sem gerar estatísticas de aluno.

- `exercicios_feitos`: exercícios distintos respondidos, mesmo sem acerto.
- `total_tentativas`: todas as respostas registradas.
- `taxa_acerto`: tentativas corretas / total de tentativas × 100; zero sem tentativas.
- `modulos_concluidos`: módulos publicados com pelo menos um exercício, todos acertados ao menos uma vez.
- `total_modulos`: módulos publicados, incluindo os ainda sem exercícios.

As tentativas são históricas: editar um gabarito não reavalia respostas antigas. Adicionar ou mover exercícios pode mudar a conclusão calculada de um módulo. Não há relação professor/turma neste modelo: professores consultam todos os estudantes, conforme UC10.

## Testes

`python -m pip install -r requirements-dev.txt` e `python -m pytest -q`.

Os testes sobrescrevem as variáveis de conexão e usam SQLite em memória. Cobrem login, assinatura/expiração, permissões, rascunhos, proteção de gabaritos, estatísticas, edição, promoção, exclusão e invalidação de acesso. A integração com MySQL deve ser verificada no ambiente de homologação.

## Hospedagem cPanel

Consulte [DEPLOY.md](DEPLOY.md) para configurar MySQL, variáveis de ambiente, domínio e execução da API no cPanel.

O plano precisa permitir um servidor ASGI como Uvicorn, execução persistente e proxy HTTPS para a API. O fluxo Python WSGI/Passenger do cPanel não confirma esse suporte. A configuração final depende da empresa e do plano contratados.

Referências: [Python no cPanel](https://docs.cpanel.net/knowledge-base/web-services/how-to-install-a-python-wsgi-application/), [ASGI no FastAPI](https://fastapi.tiangolo.com/deployment/manually/).
