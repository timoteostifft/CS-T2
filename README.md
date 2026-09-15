# Recomendações API

API para busca de lugares e envio de avaliações e sugestões de atividades pelos usuários.

Construída com [FastAPI](https://fastapi.tiangolo.com/) seguindo uma **Arquitetura Hexagonal** (Ports & Adapters): as regras de negócio vivem em `domain/`, isoladas dos detalhes de infraestrutura (HTTP, banco de dados) através de interfaces (`ports`) implementadas por `adapters` intercambiáveis.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — gerenciador de dependências e projeto

Instalar o `uv` (macOS/Linux):

```bash
brew install uv
```

## Setup

Clone o repositório e instale as dependências:

```bash
uv sync
```

Isso cria um `.venv` local e instala todas as dependências travadas em `uv.lock` — sem precisar criar venv ou rodar `pip install` manualmente.

## Rodando a API

```bash
uv run fastapi dev src/recomendacoes_api/app.py
```

O servidor sobe em `http://127.0.0.1:8000` com hot-reload habilitado.

Documentação interativa:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Exemplo de requisição

```bash
curl http://127.0.0.1:8000/places
```

## Rodando os testes

```bash
uv run pytest -v
```

Os testes são organizados por camada:

- `tests/domain/` — entidades testadas isoladamente, sem framework ou infraestrutura envolvida.
- `tests/application/` — use cases testados com um repositório fake, sem precisar de banco de dados ou servidor HTTP.

## Arquitetura

Este projeto segue a **Arquitetura Hexagonal** (também conhecida como Ports & Adapters). A ideia central: as regras de negócio vivem isoladas em um **domínio**, sem conhecimento de frameworks, bancos de dados ou HTTP — tudo que é externo se conecta a ele através de interfaces explícitas (**ports**), implementadas por **adapters** intercambiáveis.

```
                    ┌──────────────────────┐
                    │   Driven Adapter     │
                    │  (adapters/database) │
                    └───────────┬──────────┘
                                │ implementa
                                ▼
┌──────────────────┐        ┌──────────────────┐
│ Driving Adapter  │──usa──►│     Domínio      │
│ (adapters/rest)  │        │ entities + ports │
└──────────────────┘        └──────────────────┘
        ▲                        ▲
        │                        │ orquestra
        └──── application/ ──────┘
```

**Regra de dependência:** as dependências sempre apontam para dentro. `domain/` nunca importa nada de `application/` ou `adapters/`. `application/` depende só de `domain/`. `adapters/` dependem dos dois, mas nem `domain/` nem `application/` sabem que esses adapters existem.

| Camada                     | Responsabilidade                                                                                                                                                     |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `domain/entities.py`       | Objetos de negócio centrais e seus invariantes (ex: `Place`). Python puro, sem imports de framework.                                                                 |
| `domain/ports.py`          | Interfaces (`Protocol`) que o domínio exige do mundo externo — ex: `PlaceRepository`. Definidas pelo domínio, implementadas em outro lugar.                          |
| `application/use_cases.py` | Orquestra entidades e ports para cumprir um caso de uso específico (ex: `ListPlacesUseCase`). Sem regra de negócio própria, sem código de framework.                 |
| `adapters/rest/`           | **Driving adapter** — traduz requisições HTTP em chamadas de use case, e objetos de domínio em respostas de API (`controllers.py`, `schemas.py`, `dependencies.py`). |
| `adapters/database/`       | **Driven adapter** — implementa as ports com um mecanismo concreto de armazenamento (atualmente em memória).                                                         |

## Estrutura do projeto

```
src/recomendacoes_api/
├── app.py                    # Entrypoint do FastAPI
├── domain/
│   ├── entities.py           # Entidades de negócio (ex: Place)
│   └── ports.py               # Interfaces que o domínio exige da infraestrutura
├── application/
│   └── use_cases.py           # Orquestra entidades de domínio para um caso de uso específico
└── adapters/
    ├── rest/                  # Driving adapter: controllers HTTP, schemas de request/response
    └── database/               # Driven adapter: implementações de repositório
```
