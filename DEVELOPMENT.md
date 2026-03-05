# Development Guide - Back IA Python

Guia para contribuir e desenvolver novos recursos.

## 📐 Arquitetura

A aplicação segue o padrão **modular em camadas**:

```
Request
   ↓
[FastAPI Router] (controllers.py)
   ↓
[Service Layer] (services.py) ← Regras de negócio
   ↓
[Data Layer] (models.py + database.py) ← Persistência
   ↓
Database (PostgreSQL)
```

---

## 🎯 Fluxo de Desenvolvimento

### 1. Criar Nova Feature

```bash
# Criar branch
git checkout -b feature/minha-feature
```

### 2. Implementar Modelo (se necessário)

Editar `src/infra/models.py`:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class MinhaEntidade(Base):
    __tablename__ = "minhas_entidades"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    # ... mais campos
```

### 3. Rodar Migração

```bash
# Gerar migração
alembic revision --autogenerate -m "Add MinhaEntidade model"

# Executar
alembic upgrade head
```

### 4. Criar Service Layer

Arquivo: `src/modules/meu_modulo/services.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from src.infra.models import MinhaEntidade

class MeuModuloService:
    @staticmethod
    async def criar(nome: str, db: AsyncSession) -> MinhaEntidade:
        entidade = MinhaEntidade(nome=nome)
        db.add(entidade)
        await db.commit()
        await db.refresh(entidade)
        return entidade
    
    @staticmethod
    async def obter_por_id(id: str, db: AsyncSession) -> MinhaEntidade:
        result = await db.execute(
            select(MinhaEntidade).where(MinhaEntidade.id == id)
        )
        entidade = result.scalar_one_or_none()
        if not entidade:
            raise NotFoundError("Entidade não encontrada")
        return entidade
```

### 5. Criar Schemas (DTOs)

Arquivo: `src/modules/meu_modulo/schemas.py`

```python
from pydantic import BaseModel, Field
from datetime import datetime

class CriarMeuModuloRequest(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)

class MeuModuloResponse(BaseModel):
    id: str
    nome: str
    created_at: datetime
    
    model_config = {"from_attributes": True}
```

### 6. Criar Controllers (Rotas)

Arquivo: `src/modules/meu_modulo/controllers.py`

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.infra.database import get_db
from src.modules.meu_modulo.services import MeuModuloService
from src.modules.meu_modulo.schemas import CriarMeuModuloRequest, MeuModuloResponse
from src.shared.security import get_current_user

router = APIRouter(
    prefix=f"/{settings.api_prefix}/meu-modulo",
    tags=["Meu Módulo"]
)

@router.post("", response_model=MeuModuloResponse, status_code=status.HTTP_201_CREATED)
async def criar(
    request: CriarMeuModuloRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cria novo item."""
    entidade = await MeuModuloService.criar(
        nome=request.nome,
        db=db
    )
    return MeuModuloResponse.model_validate(entidade)

@router.get("/{id}", response_model=MeuModuloResponse)
async def obter(
    id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtém item por ID."""
    entidade = await MeuModuloService.obter_por_id(id, db)
    return MeuModuloResponse.model_validate(entidade)
```

### 7. Registrar Router

Editar `src/main.py`:

```python
from src.modules.meu_modulo.controllers import router as meu_modulo_router

app.include_router(meu_modulo_router)
```

### 8. Escrever Testes

Arquivo: `tests/test_meu_modulo.py`

```python
import pytest

@pytest.mark.asyncio
async def test_criar_item(test_client):
    """Testa criação de item."""
    response = test_client.post(
        "/v1/meu-modulo",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"nome": "Teste"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Teste"

@pytest.mark.asyncio
async def test_obter_item(test_client):
    """Testa obtenção de item."""
    # Criar item
    create_response = test_client.post(...)
    item_id = create_response.json()["id"]
    
    # Obter item
    response = test_client.get(f"/v1/meu-modulo/{item_id}")
    assert response.status_code == 200
```

### 9. Rodar Testes

```bash
pytest tests/test_meu_modulo.py -v

# Com cobertura
pytest tests/test_meu_modulo.py --cov=src.modules.meu_modulo
```

### 10. Commit e Push

```bash
git add .
git commit -m "feat: adiciona módulo de meu-modulo"
git push origin feature/minha-feature
```

---

## 🧩 Padrões de Código

### Exception Handling

```python
from src.shared.exceptions import (
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
)

# Uso
if not user:
    raise NotFoundError("Usuário não encontrado")

if user.role != "ADMIN":
    raise ForbiddenError("Acesso restrito a administradores")

if email_existe:
    raise ConflictError("Email já foi registrado")
```

### Async/Await

Sempre usar **async/await** com SQLAlchemy:

```python
# ❌ Errado
user = db.query(User).filter_by(id=user_id).first()

# ✅ Correto
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
```

### Type Hints

Sempre usar type hints:

```python
# ❌ Errado
async def criar(nome, email, db):
    pass

# ✅ Correto
async def criar(
    nome: str,
    email: str,
    db: AsyncSession,
) -> User:
    pass
```

### Validação com Pydantic

```python
from pydantic import BaseModel, Field, field_validator

class CriarUserRequest(BaseModel):
    email: str = Field(..., min_length=5)
    phone: str
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        clean = "".join(filter(str.isdigit, value))
        if len(clean) != 11:
            raise ValueError("Telefone deve ter 11 dígitos")
        return clean
```

---

## 🔐 Segurança

### Proteção de Rotas

```python
# Apenas usuários autenticados
@router.get("/protegido")
async def rota_protegida(
    current_user: dict = Depends(get_current_user),
):
    return {"user_id": current_user["sub"]}

# Apenas ADMINs
@router.delete("/usuarios/{id}")
async def deletar_usuario(
    id: str,
    current_user: dict = Depends(require_admin),
):
    # Apenas ADMIN consegue deletar
    pass
```

### Validação de Entrada

Sempre validar entrada com Pydantic + Field validators

### Nunca logar senhas

```python
# ❌ Errado
logger.info(f"Login: {email}, Senha: {password}")

# ✅ Correto
logger.info(f"Login attempt: {email}")
```

---

## 📊 Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Usuário criado", extra={"user_id": user.id})
logger.warning("Tentativa de acesso não autorizado")
logger.error("Falha ao conectar com banco", exc_info=True)
```

---

## 🧪 Testes

### Structure

```
tests/
  ├── conftest.py           # Fixtures shared
  ├── test_auth.py          # Testes de auth
  ├── test_health.py        # Testes de health
  └── ...
```

### Fixtures Úteis

```python
@pytest.fixture
async def test_user(test_session):
    """Cria usuário de teste."""
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=hash_password("password123")
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user

@pytest.fixture
def auth_header(test_user):
    """Gera header com token válido."""
    token = create_access_token(
        str(test_user.id),
        test_user.email,
        test_user.role.value
    )
    return {"Authorization": f"Bearer {token}"}
```

### Assertions

```python
assert response.status_code == 200
assert response.json()["email"] == "test@example.com"
assert "access_token" in response.json()
```

---

## 🚀 Performance

### Query Optimization

```python
# ❌ N+1 query problem
users = await db.execute(select(User))
for user in users:
    posts = user.posts  # Query executada para cada user!

# ✅ Use joinedload
from sqlalchemy.orm import joinedload

result = await db.execute(
    select(User).options(joinedload(User.posts))
)
users = result.unique().scalars().all()
```

### Indexing

```python
email: Mapped[str] = mapped_column(
    String(255),
    unique=True,
    nullable=False,
    index=True  # ← Adicionar índice
)
```

---

## 📝 Docstrings

```python
async def criar_usuario(
    email: str,
    password: str,
    db: AsyncSession,
) -> User:
    """Cria novo usuário com email e senha.
    
    Args:
        email: Email único do usuário
        password: Senha em texto plano (será hasheada)
        db: Sessão do banco de dados
        
    Returns:
        User: Usuário recém-criado
        
    Raises:
        ConflictError: Se email já existe
        ValidationError: Se entrada inválida
    """
    # implementação
    pass
```

---

## 🔍 Code Review Checklist

- [ ] Código segue padrões do projeto
- [ ] Type hints completos
- [ ] Testes funcionando
- [ ] Sem logs sensíveis (senhas, tokens)
- [ ] Async/await correto
- [ ] DTOs validando entrada
- [ ] Exceções apropriadas lançadas
- [ ] Documentação atualizada

---

## 📚 Recursos Úteis

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/20/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [JWT Guide](https://jwt.io/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

**Last updated**: 5 de março de 2026
