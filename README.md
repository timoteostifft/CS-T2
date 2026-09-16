# Recomendações API

[![CI](https://github.com/timoteostifft/CS-T2/actions/workflows/ci.yml/badge.svg)](https://github.com/timoteostifft/CS-T2/actions/workflows/ci.yml)

API para busca de lugares e envio de avaliações e sugestões de atividades pelos usuários.

Construída com [FastAPI](https://fastapi.tiangolo.com/) seguindo uma **Arquitetura Hexagonal** (Ports & Adapters): as regras de negócio vivem em `domain/`, isoladas dos detalhes de infraestrutura (HTTP, banco de dados) através de interfaces (`ports/`) implementadas por `adapters/` intercambiáveis.

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
- `tests/application/` — use cases testados com um repositório mock, sem precisar de banco de dados ou servidor HTTP.
- `tests/adapters/rest/` — endpoints testados via `TestClient`, com `dependency_overrides` para injetar mocks.

## Lint e formatação

```bash
uv run ruff check .      # lint
uv run ruff format .     # formata o código
```

Configurado em `[tool.ruff]` no `pyproject.toml` (line length 100, regras de pyflakes/pycodestyle/isort/pyupgrade/bugbear).

## Arquitetura

Este projeto segue a **Arquitetura Hexagonal** (também conhecida como Ports & Adapters). A ideia central: as regras de negócio vivem isoladas em um **domínio**, sem conhecimento de frameworks, bancos de dados ou HTTP — tudo que é externo se conecta a ele através de interfaces explícitas (**ports**), implementadas por **adapters** intercambiáveis. As ports ficam em um pacote próprio, `ports/`, separado do `domain/`, para deixar visualmente clara a fronteira entre "o que o domínio é" (entities, exceptions) e "o que o domínio exige do mundo externo" (contratos).

```
                    ┌──────────────────────┐
                    │   Driven Adapter     │
                    │  (adapters/database) │
                    └───────────┬──────────┘
                                │ implementa
                                ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ Driving Adapter  │──usa──►│     ports/       │◄──usa──│     Domínio      │
│ (adapters/rest)  │        │  (contratos)      │        │  entities +      │
└──────────────────┘        └──────────────────┘        │  exceptions      │
        ▲                                                └──────────────────┘
        │                        ▲
        │                        │ orquestra
        └──── application/ ──────┘
```

**Regra de dependência:** as dependências sempre apontam para dentro. `domain/` nunca importa nada de `ports/`, `application/` ou `adapters/`. `ports/` depende só de `domain/` (para tipar os métodos com as entidades). `application/` depende de `domain/` e `ports/`. `adapters/` dependem de todos os anteriores, mas nenhum deles sabe que os adapters existem.

| Camada                          | Responsabilidade                                                                                                                                                     |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `domain/entities.py`             | Objetos de negócio centrais e seus invariantes (ex: `Place`). Python puro, sem imports de framework.                                                                 |
| `domain/exceptions.py`           | Exceções de negócio (ex: `InvalidPlaceError`), uma por tipo de erro, levantadas pelas entidades ou pelos use cases.                                                  |
| `ports/repositories.py`          | Interfaces (`Protocol`) que o domínio exige do mundo externo — ex: `PlaceRepository`. Definidas para a aplicação, implementadas nos adapters.                        |
| `application/use_cases.py`       | Orquestra entidades e ports para cumprir um caso de uso específico (ex: `ListPlacesUseCase`). Sem regra de negócio própria, sem código de framework.                 |
| `adapters/rest/`                 | **Driving adapter** — traduz requisições HTTP em chamadas de use case, objetos de domínio em respostas de API, e exceções de domínio em respostas HTTP de erro.      |
| `adapters/database/`             | **Driven adapter** — implementa as ports com um mecanismo concreto de armazenamento (atualmente em memória).                                                         |

## Estrutura do projeto

```
src/recomendacoes_api/
├── app.py                       # Entrypoint do FastAPI
├── domain/
│   ├── entities.py              # Entidades de negócio (ex: Place)
│   └── exceptions.py             # Exceções de negócio (ex: InvalidPlaceError)
├── ports/
│   └── repositories.py           # Interfaces que a aplicação exige da infraestrutura
├── application/
│   └── use_cases.py              # Orquestra entidades de domínio para um caso de uso específico
└── adapters/
    ├── rest/                     # Driving adapter: controllers HTTP, schemas, exception handlers
    └── database/                  # Driven adapter: implementações de repositório
```
