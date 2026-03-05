# Documentação — Backend Python (REST + JWT + PostgreSQL)

<aside>
✅

**Objetivo**

Criar um backend em Python com API REST, autenticação via JWT e persistência em PostgreSQL, com foco em manutenção simples e padrão de projeto claro.

</aside>

### Stack sugerida (fácil manutenção)

- **FastAPI 0.104+**
- **SQLAlchemy 2.0+**
- **Alembic**
- **pytest + pytest-asyncio**
- **PyJWT + python-jose**
- **argon2-cffi** (mais seguro que bcrypt)
- **Swagger** (automático no FastAPI)
- **Docker + docker-compose**

---

### Arquitetura (visão geral)

- **Módulos** por domínio (ex.: `auth`, `users`, `health`).
- **Camadas**:
    - Controller (HTTP)
    - Service (regras de negócio)
    - Repository/Prisma (persistência)
- **Validação** com DTOs (class-validator).
- **Configuração** por variáveis de ambiente (12-factor).

---

### Requisitos não-funcionais

- Logs estruturados (mínimo: requestId, método, path, status, tempo).
- Tratamento padronizado de erros (HTTP status + payload consistente).
- CORS configurável.
- Versionamento de rota: `/v1/...`.
- Healthcheck para monitoramento.

---

### Modelo de dados (MVP)

**User**

- `id` (UUID)
- `name` (string)
- `email` (string, unique)
- `cpf_cnpj` (number, max 14, unique)
- `celular` (string, max 11, unique)
- `passwordHash` (string)
- `role` (enum: `ADMIN`, `USER`)
- `createdAt`, `updatedAt`

---

### Autenticação e autorização

#### JWT

- **Access token** assinado com `JWT_SECRET`.
- **Expiração** recomendada: 15m–60m.
- Payload mínimo: `sub` (userId), `email`, `role`.

#### Proteção de rotas

- Guard middleware que valida `Authorization: Bearer <token>`.
- Decorator para role (ex.: `@Roles('ADMIN')`) quando necessário.

---

### Endpoints (MVP)

Base URL: `https://<host>/v1`

#### Auth

- `POST /auth/register`
    - Cria usuário.
- `POST /auth/login`
    - Retorna `accessToken`.
- `GET /auth/me` *(protegido)*
    - Retorna dados do usuário autenticado.

#### Users *(exemplo de CRUD básico)*

- `GET /users` *(protegido, opcional ADMIN)*
- `GET /users/:id` *(protegido)*
- `POST /users` *(protegido, ADMIN)*
- `PATCH /users/:id` *(protegido)*
- `DELETE /users/:id` *(protegido, ADMIN)*

#### Health

- `GET /health`
    - Retorna status do serviço e conectividade com DB.

---

### Contratos (exemplos)

#### POST /auth/login

Request:

```json
{
  "email": "user@exemplo.com",
  "password": "123456"
}
```

Response (200):

```json
{
  "accessToken": "<jwt>",
  "tokenType": "Bearer",
  "expiresIn": 3600
}
```

---

### Padronização de erros

Payload recomendado:

```json
{
  "statusCode": 400,
  "error": "Bad Request",
  "message": ["email must be an email"],
  "path": "/v1/auth/register",
  "timestamp": "2026-02-27T19:23:22.599Z"
}
```

---

### Variáveis de ambiente

```bash
# App
NODE_ENV=development
PORT=3000
API_PREFIX=v1

# JWT
JWT_SECRET=change-me
JWT_EXPIRES_IN=3600

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app?schema=public
```

---

### Docker (ambiente local)

`docker-compose.yml` (esqueleto):

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

---

### Estrutura sugerida do projeto

```
src/
  main.ts
  app.module.ts
  modules/
    auth/
      auth.controller.ts
      auth.service.ts
      jwt.strategy.ts
      dto/
    users/
      users.controller.ts
      users.service.ts
      dto/
  infra/
    prisma/
      prisma.module.ts
      prisma.service.ts
prisma/
  schema.prisma
```

---

### Prisma (exemplo de schema)

```jsx
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

enum Role {
  ADMIN
  USER
}

model User {
  id           String   @id @default(uuid())
  name         String
  email        String   @unique
  cpf_cnpj     String   @unique @db.VarChar(14)
  celular      String   @unique @db.VarChar(11)
  passwordHash String
  role         Role     @default(USER)
  createdAt    DateTime @default(now())
  updatedAt    DateTime @updatedAt
}
```

---

### Refresh Token (obrigatório)

- Implementar **refresh token** para sessão longa.
- `POST /auth/login`: retornar `accessToken` + `refreshToken`.
- `POST /auth/refresh`: trocar `refreshToken` por novo `accessToken` (e opcionalmente rotacionar refresh).
- `POST /auth/logout`: invalidar refresh token (ex.: apagar/revogar no DB).

### CRUD de Users (restrições)

- O usuário **não poderá editar dados de perfil** (nome, email, celular, cpf/cnpj etc.).
- O usuário poderá **somente cadastrar uma nova senha**.
    - Sugestão de rota: `PATCH /users/:id/password` (protegida, somente o próprio usuário).
    - Alternativa: `POST /auth/change-password` (protegida).

### Validação de email e celular (tokens únicos)

- No CRUD de `users`, **email e celular devem ser validados** via envio e recepção de **tokens únicos**.
    - Gerar token único por canal (email e SMS/WhatsApp) com expiração.
    - Fluxo sugerido:
        - `POST /auth/verify/email/request` (envia token)
        - `POST /auth/verify/email/confirm` (confirma token)
        - `POST /auth/verify/phone/request` (envia token)
        - `POST /auth/verify/phone/confirm` (confirma token)
    - Armazenar hash do token + expiração + status (pendente/validado) por usuário.

### Próximas decisões (para fechar o escopo)

1. Refresh token: **stateless** (somente JWT). ✅
2. Token de validação: **SMS** e **Telegram**. ✅