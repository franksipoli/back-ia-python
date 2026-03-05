# 🚀 DEPLOYMENT GUIDE - Backend Python FastAPI

---

## 📋 PRÉ-REQUISITOS

### Sistema
- Linux/macOS ou WSL2 (Windows)
- Python 3.10+
- PostgreSQL 15+ ou suporte para Docker

### Instalação Local
```bash
# 1. Python
python3 --version  # Verificar >= 3.10

# 2. Dependências do sistema
pip3 install -r requirements.txt

# 3. PostgreSQL (via Docker)
docker run -d \
  --name postgres_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=back_ia_db \
  -p 5432:5432 \
  postgres:15
```

---

## 🔧 SETUP INICIAL

### 1. Variáveis de Ambiente
```bash
# Criar arquivo .env
cp .env.example .env

# Configurar (exemplo)
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/back_ia_db

# JWT
JWT_SECRET=sua_chave_super_secreta_min_32_chars
JWT_EXPIRES_IN=3600
JWT_EXPIRES_IN_REFRESH=604800

# App
DEBUG=True
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF
```

### 2. Banco de Dados
```bash
# Aplicar migrações
alembic upgrade head

# Verificar tabelas
psql -U postgres -h localhost -d back_ia_db -c "\dt"

# Saída esperada:
# users | public | table
# refresh_tokens | public | table
# email_verifications | public | table
# phone_verifications | public | table
```

### 3. Criar Usuário Admin (Opcional)
```bash
python3 << 'EOF'
import sys
import asyncio
from src.modules.auth.services import AuthService
from src.infra.database import get_db_session

async def create_admin():
    async with get_db_session() as session:
        service = AuthService(session)
        user = await service.register(
            name="Admin",
            email="admin@exemplo.com",
            cpf_cnpj="12345678901234",
            celular="11999999999",
            password="Admin@123",
            role="ADMIN"
        )
        print(f"✅ Admin criado: {user.email}")

asyncio.run(create_admin())
EOF
```

---

## 🏃 EXECUTAR LOCALMENTE

### Desenvolvimento
```bash
# Terminal 1: Backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Testes (opcional)
pytest -v --tb=short
```

### Acesso
```
API: http://localhost:8000/v1
Swagger Docs: http://localhost:8000/v1/docs
ReDoc: http://localhost:8000/v1/redoc
```

---

## 🐳 DOCKER - PRODUÇÃO

### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Migrations
RUN alembic upgrade head

# Porta
EXPOSE 8000

# Iniciar aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: back_ia_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: back_ia_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    container_name: back_ia_api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/back_ia_db
      JWT_SECRET: ${JWT_SECRET}
      DEBUG: "False"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./src:/app/src
      - ./migrations:/app/migrations

volumes:
  pgdata:
```

### Iniciar com Docker Compose
```bash
# Build e iniciar
docker-compose up --build

# Verificar logs
docker-compose logs -f api

# Parar
docker-compose down
```

---

## ☁️ DEPLOYMENT EM CLOUD

### Azure App Service (Recomendado)

#### 1. Preparar Aplicação
```bash
# Criar requirements.txt com versões fixas
pip freeze > requirements.txt

# Verificar Procfile
cat > Procfile << 'EOF'
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
EOF
```

#### 2. Azure CLI Setup
```bash
# Login
az login

# Criar grupo de recursos
az group create --name rg-back-ia --location brazilsouth

# Criar plano de serviço
az appservice plan create \
  --name plan-back-ia \
  --resource-group rg-back-ia \
  --sku B2 \
  --is-linux

# Criar app
az webapp create \
  --resource-group rg-back-ia \
  --plan plan-back-ia \
  --name app-back-ia \
  --runtime "PYTHON:3.10"

# Deploy código
az webapp deployment source config-zip \
  --resource-group rg-back-ia \
  --name app-back-ia \
  --src app.zip
```

#### 3. Configurar Banco de Dados
```bash
# Azure Database for PostgreSQL
az postgres server create \
  --resource-group rg-back-ia \
  --name postgresql-back-ia \
  --location brazilsouth \
  --admin-user pgadmin \
  --admin-password <senha-forte>

# Variáveis de ambiente na app
az webapp config appsettings set \
  --resource-group rg-back-ia \
  --name app-back-ia \
  --settings \
    DATABASE_URL="postgresql://user:pass@host:5432/db" \
    JWT_SECRET="chave-super-secreta" \
    DEBUG="False"
```

#### 4. Configurar SSL
```bash
# Let's Encrypt automático (App Service)
# Já vem ativado por padrão na maioria dos plans
az webapp config ssl create \
  --resource-group rg-back-ia \
  --name app-back-ia
```

### AWS EC2 (Alternativa)

```bash
# SSH para instância
ssh -i key.pem ubuntu@<ip>

# Instalar dependências
sudo apt update && sudo apt install -y \
  python3.10 \
  postgresql-client \
  nginx

# Clone repositório
git clone <repo> /app
cd /app

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Rodar com systemd
sudo tee /etc/systemd/system/back-ia.service > /dev/null <<EOF
[Unit]
Description=Back IA API
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/app
ExecStart=/app/venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Ativar
sudo systemctl daemon-reload
sudo systemctl enable back-ia
sudo systemctl start back-ia
```

---

## 🔐 SEGURANÇA EM PRODUÇÃO

### Checklist
```
✅ Variáveis de ambiente seguras (use Secret Manager)
✅ JWT_SECRET mínimo 32 caracteres aleatórios
✅ HTTPS obrigatório (SSL/TLS)
✅ CORS apenas origens conhecidas
✅ Rate limiting ativado
✅ Logs sem dados sensíveis
✅ Database backups automáticos
✅ Monitoramento de uptime
✅ Alertas de erro configurados
```

### Exemplo .env Produção
```bash
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING

# JWT
JWT_SECRET=$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/app

# CORS
ALLOWED_ORIGINS=https://seudominio.com,https://www.seudominio.com

# Email (quando implementado)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu@email.com
SMTP_PASSWORD=senha-app

# Telegram (quando implementado)
TELEGRAM_BOT_TOKEN=seu-bot-token
TELEGRAM_ADMIN_CHAT_ID=seu-chat-id
```

---

## 📊 MONITORAMENTO

### Logs Estruturados
```bash
# Ver logs do app
tail -f /var/log/back-ia/app.log

# Com grep
grep "error\|ERROR" /var/log/back-ia/app.log

# JSON parsing (jq)
cat /var/log/back-ia/app.json | jq '.[] | select(.level=="ERROR")'
```

### Health Check
```bash
# Verificar status
curl http://localhost:8000/health

# Em produção (cada 30s)
curl -f https://seudominio.com/v1/health || systemctl restart back-ia
```

### Métricas (Prometheus - Opcional)
```bash
# Instalar prometheus client
pip install prometheus-client

# Adicionar ao main.py
from prometheus_client import Counter, Histogram, generate_latest

# Acessar em /metrics
```

---

## 🔄 CI/CD - GitHub Actions

### .github/workflows/deploy.yml
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: pytest -v
      
      - name: Build Docker image
        run: docker build -t app:latest .
      
      - name: Push to Azure Container Registry
        run: |
          docker login -u ${{ secrets.ACR_USERNAME }} -p ${{ secrets.ACR_PASSWORD }}
          docker tag app:latest ${{ secrets.ACR_LOGIN_SERVER }}/app:latest
          docker push ${{ secrets.ACR_LOGIN_SERVER }}/app:latest
      
      - name: Deploy to Azure App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: 'app-back-ia'
          publish-profile: ${{ secrets.AZURE_PUBLISH_PROFILE }}
          images: '${{ secrets.ACR_LOGIN_SERVER }}/app:latest'
```

---

## 🆘 TROUBLESHOOTING

### Erro: Connection refused (5432)
```bash
# Verificar PostgreSQL
docker ps | grep postgres

# Reiniciar
docker restart postgres_db

# Ou criar novo
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  postgres:15
```

### Erro: Token expirado
```bash
# Usar refresh token
curl -X POST http://localhost:8000/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "..."}'
```

### Erro: 403 Forbidden
```bash
# Usuário não tem permissão
# Verificar role do usuário
curl -X GET http://localhost:8000/v1/auth/me \
  -H "Authorization: Bearer {token}"

# Se necessário, dar acesso de ADMIN
# Conectar ao banco e fazer UPDATE
psql -U postgres -h localhost -d back_ia_db
UPDATE users SET role='ADMIN' WHERE email='seu@email.com';
```

### Erro: CORS bloqueado
```bash
# Adicionar origem ao .env
ALLOWED_ORIGINS=https://seudominio.com

# Ou abrir localmente (desenvolvimento)
ALLOWED_ORIGINS=*
```

---

## 📈 UPGRADES E ROLLBACK

### Upgrade de Versão
```bash
# 1. Backup database
pg_dump -U postgres back_ia_db > backup.sql

# 2. Parar app
systemctl stop back-ia

# 3. Update código
git pull origin main

# 4. Instalar novas dependências
pip install -r requirements.txt --upgrade

# 5. Migrations
alembic upgrade head

# 6. Iniciar app
systemctl start back-ia

# 7. Verificar health
curl http://localhost:8000/health
```

### Rollback
```bash
# 1. Parar app
systemctl stop back-ia

# 2. Reverter código
git revert HEAD
git push

# 3. Reverter migrations
alembic downgrade -1

# 4. Restaurar database (se necessário)
psql -U postgres < backup.sql

# 5. Iniciar app
systemctl start back-ia
```

---

## 📞 SUPORTE E CONTATO

- Documentação: `/v1/docs`
- Issues: GitHub
- Email: suporte@seudominio.com
- Status: https://status.seudominio.com

---

**Última atualização**: 05/03/2026  
**Ambiente**: Production Ready  
**Status**: ✅ Operacional
