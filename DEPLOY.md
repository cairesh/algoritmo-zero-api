# Publicação no cPanel

Destino: React estático e MySQL na hospedagem cPanel. A execução da API FastAPI depende do suporte do plano a ASGI/Uvicorn. O projeto não utiliza Supabase.

## Front-end

1. Confira a raiz de documentos de `algoritmozero.com.br` em Domains. Geralmente é `public_html`, mas use o caminho exibido para o domínio.
2. Antes do build, configure `.env.production.local` na sua máquina:

   ```env
   VITE_API_URL=https://api.algoritmozero.com.br
   ```

   Esse endereço é uma proposta: só funcionará após configurar o subdomínio e a API. Nunca coloque segredos nas variáveis `VITE_`.
3. Execute `npm ci` e `npm run build` localmente.
4. Envie o **conteúdo** de `dist/` para a raiz do domínio, incluindo `.htaccess`. Ative a exibição de arquivos ocultos no gerenciador de arquivos. Não envie `.env`, código da API ou `node_modules` para essa pasta pública.
5. Se já existir `.htaccess`, integre as regras da SPA preservando as regras da hospedagem. `public/.htaccess` é copiado pelo Vite para `dist/` e permite recarregar `/dashboard` e `/admin` em Apache com `mod_rewrite` habilitado.
6. Configure DNS e HTTPS conforme o provedor. Este guia considera o front na raiz do domínio, não em subpasta.

Mudanças em `VITE_API_URL` exigem novo build e envio dos arquivos.

## MySQL

Crie banco e usuário na ferramenta MySQL do cPanel e associe o usuário ao banco com as permissões necessárias à aplicação. Use os nomes completos exibidos, incluindo prefixos da conta.

Configure somente no ambiente privado da API:

```env
DATABASE_URL=mysql+pymysql://conta_usuario:SENHA_CODIFICADA@HOST_MYSQL:3306/conta_banco
JWT_SECRET_KEY=CHAVE_ALEATORIA_EXCLUSIVA_DE_PRODUCAO
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=https://algoritmozero.com.br,https://www.algoritmozero.com.br
```

Substitua host, usuário, senha e banco pelos dados da hospedagem. Caracteres reservados na senha precisam de codificação de URL. Liste em `CORS_ORIGINS` apenas as origens utilizadas, sem barra final. Faça backup antes de importar dados existentes. Tabelas ausentes são criadas ao iniciar a API; isso não migra alterações em tabelas existentes.

## API: confirmar suporte do plano

FastAPI requer ASGI, como Uvicorn. O fluxo Python documentado pelo cPanel usa WSGI/Passenger; ter “Setup Python App” não confirma compatibilidade direta. Não configure `app.main:app` como aplicação WSGI.

Confirme com o provedor:

- Python compatível com as dependências (recomendado 3.12 ou superior).
- Execução persistente de Uvicorn com reinício automático.
- Proxy do subdomínio HTTPS `api.algoritmozero.com.br` para esse processo, preservando `Authorization`.
- Instalação de dependências Python e acesso ao MySQL.

Com suporte confirmado, mantenha a API fora da raiz pública, crie um ambiente virtual, instale `requirements.txt` e configure as variáveis acima. Para um proxy no mesmo servidor, o comando base é:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

A porta e o gerenciador do processo devem seguir a configuração do provedor. Não use `--reload` em produção. SSH sozinho não garante permissão para processos persistentes. Se o plano oferecer apenas WSGI, será necessário definir uma adaptação ou alterar o suporte de execução antes de publicar a API.

## Verificação após publicar

Teste HTTPS, cadastro/login, envio do token, exercícios, desempenho e permissões. Recarregue `/dashboard` e `/admin` diretamente. Verifique reinício automático da API e ausência de erros de CORS.

Nenhum upload, serviço remoto ou alteração de DNS foi realizado. A configuração final da API depende da empresa e do plano de hospedagem.

Referências: [raiz de documentos no cPanel](https://docs.cpanel.net/cpanel/domains/domains/manage-the-domain/110/), [Python WSGI no cPanel](https://docs.cpanel.net/knowledge-base/web-services/how-to-install-a-python-wsgi-application/), [ASGI no FastAPI](https://fastapi.tiangolo.com/deployment/manually/).
