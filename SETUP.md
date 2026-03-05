# Setup Guide - Back IA Python

Guia completo para setup, desenvolvimento e deployment do backend.

## 🚀 Quick Start (Local)

### 1. Ambiente Virtual

```bash
# Criar venv
python3 -m venv venv

# Ativar venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
# Editar .env com valores locais
```

### 4. Banco de Dados

```bash
# Opção 1: Docker (recomendado)
docker-compose up -d db

# Opção 2: PostgreSQL local
# Certifique-se de que PostgreSQL 15+ está instalado
# DATABASE_URL deve estar correto em .env
```

### 5. Migrações

```bash
# Executar migrações
alembic upgrade head
```

### 6. Executar Aplicação

```bash
# Desenvolvimento (reload automático)
python -m uvicorn src.main:app --reload

# Produção
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

A API estará em: **http://localhost:8000**  
Docs (Swagger): **http://localhost:8000/v1/docs**  
ReDoc: **http://localhost:8000/v1/redoc**

---

## 🐳 Com Docker Compose

```bash
# Inicia tudo (API + PostgreSQL)
docker-compose up

# Logs em tempo real
docker-compose logs -f api

# Parar tudo
docker-compose down

# Remover volumes (limpar dados)
docker-compose down -v
```

---

## 🧪 Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src

# Testes específicos
pytest tests/test_auth.py -v

# Modo watch (reexecuta a cada mudança)
pip install pytest-watch
ptw
```

---

## 📝 Desenvolvimento

### Criar Nova Migração

Após modificar modelos em `src/infra/models.py`:

```bash
# Gerar migração automática
alembic revision --autogenerate -m "Descrição da mudança"

# Executar
alembic upgrade head
```

### Adicionar Novo Módulo

```
src/modules/novo_modulo/
  __init__.py
  controllers.py    # Rotas
  services.py       # Lógica de negócio
  schemas.py        # DTOs (Pydantic)
```

Depois registrar router em `src/main.py`:

```python
from src.modules.novo_modulo.controllers import router as novo_router
app.include_router(novo_router)
```

### Code Quality

```bash
# Formatação (Black)
black src/ tests/

# Lint (Ruff)
ruff check src/

# Type checking (MyPy)
mypy src/

# Tudo junto
black src/ tests/ && ruff check src/ && mypy src/
```

---

## 📚 Estrutura do Projeto

```
src/
  ├── main.py                 # App FastAPI
  ├── config.py              # Config por ambiente
  ├── modules/
  │   ├── auth/              # Autenticação
  │   │   ├── controllers.py
  │   │   ├── services.py
  │   │   └── schemas.py
  │   ├── users/             # CRUD de usuários
  │   ├── health/            # Health check
  ├── infra/                 # Infraestrutura
  │   ├── database.py        # SQLAlchemy config
  │   └── models.py          # Modelos ORM
  ├── shared/                # Shared utilities
  │   ├── exceptions.py      # Exceções custom
  │   ├── middleware.py      # Middleware (logging, error)
  │   └── security.py        # JWT, hashing

tests/
  ├── conftest.py            # Pytest config
  ├── test_auth.py
  ├── test_health.py
  └── ...

migrations/
  ├── env.py                 # Alembic config
  ├── script.py.mako         # Migration template
  └── versions/              # Migration files
```

---

## 🔑 Autenticação JWT

### Fluxo Login

1. **POST `/v1/auth/login`** → retorna `accessToken` + `refreshToken`
2. Token é enviado em **`Authorization: Bearer <token>`** em requisições protegidas
3. Access token expira em 1h (configurável em `.env`)
4. Usar **`POST /v1/auth/refresh`** para renovar

### Headers

```bash
# Protected endpoints
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/v1/users
```

---

## 📋 Endpoints Principais

### 🔐 Auth

| Método | Rota | Protegido | Descrição |
|--------|------|-----------|-----------|
| POST | `/v1/auth/register` | ❌ | Registrar novo usuário |
| POST | `/v1/auth/login` | ❌ | Login (retorna tokens) |
| POST | `/v1/auth/refresh` | ❌ | Renovar access token |
| POST | `/v1/auth/logout` | ❌ | Logout (revoga refresh token) |
| GET | `/v1/auth/me` | ✅ | Dados do usuário autenticado |
| PATCH | `/v1/auth/me/password` | ✅ | Alterar senha |

### 👥 Users

| Método | Rota | Protegido | Permissão |
|--------|------|-----------|-----------|
| GET | `/v1/users` | ✅ | ADMIN |
| GET | `/v1/users/{id}` | ✅ | Próprio ou ADMIN |
| POST | `/v1/users` | ✅ | ADMIN |
| PATCH | `/v1/users/{id}` | ✅ | ADMIN |
| DELETE | `/v1/users/{id}` | ✅ | ADMIN |

### 🏥 Health

| Método | Rota | Protegido |
|--------|------|-----------|
| GET | `/v1/health` | ❌ |

---

## 🔒 Variáveis de Ambiente

```bash
# Aplicação
PYTHON_ENV=development              # development|testing|production
PORT=8000
API_PREFIX=v1

# JWT
JWT_SECRET=seu-secret-complexo-aqui  # ⚠️ Mudar em produção!
JWT_EXPIRES_IN=3600                  # 1 hora
JWT_ALGORITHM=HS256
REFRESH_TOKEN_EXPIRES_IN=604800      # 7 dias

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db_name

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

---

## 🚨 Troubleshooting

### Erro: "psycopg2: connection refused"
- Banco não está rodando. Execute: `docker-compose up -d db`

### Erro: "alembic.util.exc.CommandError: Can't locate revision identified by…"
- Banco está desincronizado. Execute: `alembic downgrade base && alembic upgrade head`

### Erro: "ModuleNotFoundError"
- Instale dependências: `pip install -r requirements.txt`

### Testes falhando
- Use banco de testes em memória (veja `conftest.py`)
- Limpe cache: `find . -type d -name __pycache__ -exec rm -r {} +`

---

## 📦 Deployment

### Environment de Produção

```bash
PYTHON_ENV=production
JWT_SECRET=gerar-secret-aleatório-complexo-aqui
DATABASE_URL=postgresql://prod_user:prod_pass@prod.db:5432/prod_db
LOG_LEVEL=WARNING
CORS_ORIGINS=https://seu-frontend.com
```

### With Docker

```bash
# Build image
docker build -t seu-app:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e PYTHON_ENV=production \
  -e JWT_SECRET=... \
  -e DATABASE_URL=... \
  seu-app:latest
```

---

## 📞 Contato / Suporte

Veja [README.md](./README.md) para mais informações.

---

**Last updated**: 5 de março de 2026
