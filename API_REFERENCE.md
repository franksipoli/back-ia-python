# 📚 REFERÊNCIA RÁPIDA - API Endpoints

## Base URL
```
http://localhost:8000/v1
```

---

## 🔐 AUTENTICAÇÃO

### 1. Registrar Novo Usuário
```bash
POST /auth/register

{
  "name": "João Silva",
  "email": "joao@exemplo.com",
  "cpf_cnpj": "12345678901234",
  "celular": "11999999999",
  "password": "Senha@123",
  "password_confirm": "Senha@123"
}

Response (201):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 2. Fazer Login
```bash
POST /auth/login

{
  "email": "joao@exemplo.com",
  "password": "Senha@123"
}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 3. Obter Dados do Usuário Autenticado
```bash
GET /auth/me
Authorization: Bearer {access_token}

Response (200):
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "João Silva",
    "email": "joao@exemplo.com",
    "cpf_cnpj": "12345678901234",
    "celular": "11999999999",
    "role": "USER",
    "is_active": true,
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z"
  }
}
```

### 4. Renovar Access Token
```bash
POST /auth/refresh

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..._NOVO",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 5. Fazer Logout
```bash
POST /auth/logout
Authorization: Bearer {access_token}

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (204): No Content
```

---

## 👥 GERENCIAMENTO DE USUÁRIOS

### 6. Listar Todos os Usuários
```bash
GET /users
Authorization: Bearer {access_token}
# ⚠️ Requer role: ADMIN

Response (200):
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "João Silva",
    "email": "joao@exemplo.com",
    "cpf_cnpj": "12345678901234",
    "celular": "11999999999",
    "role": "USER",
    "is_active": true,
    "created_at": "2026-03-05T10:00:00Z",
    "updated_at": "2026-03-05T10:00:00Z"
  }
]
```

### 7. Obter Usuário por ID
```bash
GET /users/{user_id}
Authorization: Bearer {access_token}

Response (200):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "João Silva",
  "email": "joao@exemplo.com",
  "cpf_cnpj": "12345678901234",
  "celular": "11999999999",
  "role": "USER",
  "is_active": true,
  "created_at": "2026-03-05T10:00:00Z",
  "updated_at": "2026-03-05T10:00:00Z"
}
```

### 8. Criar Novo Usuário (ADMIN)
```bash
POST /users
Authorization: Bearer {access_token}
# ⚠️ Requer role: ADMIN

{
  "name": "Maria Clara",
  "email": "maria@exemplo.com",
  "cpf_cnpj": "98765432109876",
  "celular": "21988888888",
  "password": "Senha@456",
  "password_confirm": "Senha@456",
  "role": "ADMIN"
}

Response (201):
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Maria Clara",
  "email": "maria@exemplo.com",
  "cpf_cnpj": "98765432109876",
  "celular": "21988888888",
  "role": "ADMIN",
  "is_active": true,
  "created_at": "2026-03-05T10:00:00Z",
  "updated_at": "2026-03-05T10:00:00Z"
}
```

### 9. Atualizar Usuário (ADMIN)
```bash
PATCH /users/{user_id}
Authorization: Bearer {access_token}
# ⚠️ Requer role: ADMIN

{
  "name": "Maria Clara Silva",
  "is_active": true
}

Response (200):
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Maria Clara Silva",
  "email": "maria@exemplo.com",
  "cpf_cnpj": "98765432109876",
  "celular": "21988888888",
  "role": "ADMIN",
  "is_active": true,
  "created_at": "2026-03-05T10:00:00Z",
  "updated_at": "2026-03-05T10:00:01Z"
}
```

### 10. Deletar Usuário (ADMIN)
```bash
DELETE /users/{user_id}
Authorization: Bearer {access_token}
# ⚠️ Requer role: ADMIN

Response (204): No Content
```

---

## 🏥 SAÚDE DA APLICAÇÃO

### 11. Health Check
```bash
GET /health

Response (200):
{
  "status": "ok",
  "environment": "development",
  "version": "0.1.0",
  "database": "healthy"
}
```

---

## 📖 DOCUMENTAÇÃO

### 12. Swagger UI
```
GET /v1/docs
Response: HTML com documentação interativa (HTTP 200)
```

### 13. ReDoc
```
GET /v1/redoc
Response: Documentação alternativa (HTTP 200)
```

---

## 🔑 AUTENTICAÇÃO

### Headers Necessários
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

### JWT Payload Exemplo
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "joao@exemplo.com",
  "role": "USER",
  "type": "access",
  "iat": 1741183200,
  "exp": 1741186800
}
```

---

## ⏱️ TEMPOS DE EXPIRAÇÃO

| Token | Duração | Segundos |
|-------|---------|----------|
| Access Token | 1 hora | 3600 |
| Refresh Token | 7 dias | 604800 |

---

## 🚨 CÓDIGOS DE ERRO

| HTTP | Significado | Exemplo |
|------|-------------|---------|
| 200 | Sucesso | GET /auth/me |
| 201 | Criado | POST /auth/register |
| 204 | Sem conteúdo | DELETE /users/:id |
| 400 | Requisição inválida | JSON malformado |
| 401 | Não autenticado | Token expirado |
| 403 | Não autorizado | Sem permissão |
| 404 | Não encontrado | ID inexistente |
| 409 | Conflito | Email duplicado |
| 422 | Validação falhou | Email inválido |
| 500 | Erro interno | Database offline |

---

## 💡 DICAS DE USO

### cURL - Registrar
```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João",
    "email": "joao@teste.com",
    "cpf_cnpj": "12345678901234",
    "celular": "11999999999",
    "password": "Senha@123",
    "password_confirm": "Senha@123"
  }'
```

### cURL - Login
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@teste.com",
    "password": "Senha@123"
  }'
```

### cURL - Rota Protegida
```bash
curl -X GET http://localhost:8000/v1/auth/me \
  -H "Authorization: Bearer {access_token}"
```

---

## 📋 VALIDAÇÕES OBRIGATÓRIAS

| Campo | Tipo | Min | Max | Regex |
|-------|------|-----|-----|-------|
| name | string | 1 | 255 | - |
| email | string | - | - | /^[^@]+@[^@]+\.[^@]+$/ |
| cpf_cnpj | string | 14 | 14 | /^\d{14}$/ |
| celular | string | 11 | 11 | /^\d{11}$/ |
| password | string | 6 | 255 | - |
| role | enum | - | - | ADMIN\|USER |

---

**Última atualização**: 05/03/2026  
**Versão API**: v1  
**Status**: ✅ Operacional
