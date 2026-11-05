# ViajaJunto API

[![CI](https://github.com/timoteostifft/CS-T2/actions/workflows/ci.yml/badge.svg)](https://github.com/timoteostifft/CS-T2/actions/workflows/ci.yml)

API de planejamento colaborativo de viagens. Usuários criam viagens com destinos, atividades e orçamento, convidam colaboradores (Editor ou Visualizador) e avaliam atividades de um catálogo público.

Os requisitos estão em [docs/requirements.md](https://github.com/ViajaJunto/template-doc-construcao-software/blob/main/docs/requirements.md). Esta versão implementa os requisitos funcionais de prioridade **Alta**.

Construída com [FastAPI](https://fastapi.tiangolo.com/) seguindo uma **Arquitetura Hexagonal** (Ports & Adapters): as regras de negócio vivem em `domain/`, isoladas dos detalhes de infraestrutura (HTTP, banco de dados) através de interfaces (`ports/`) implementadas por `adapters/` intercambiáveis.

## Requisitos

- [Docker](https://www.docker.com/) e Docker Compose — forma recomendada de rodar (API + Postgres já configurados)
- Ou, para rodar localmente sem Docker: Python 3.12+, [uv](https://docs.astral.sh/uv/), e um Postgres acessível

Instalar o `uv` (macOS/Linux), se for rodar sem Docker:

```bash
brew install uv
```

## Rodando com Docker (recomendado)

```bash
docker compose up --build
```

Isso sobe dois containers: a API (`api`, porta `8000`) e um Postgres padrão (`db`, porta `5432`, usuário/senha/banco `postgres`/`postgres`/`recomendacoes`). Na inicialização, a API cria as tabelas automaticamente (sem dados de exemplo). Como não há migrations, ao atualizar para uma versão com colunas ou tabelas novas é preciso recriar o volume (`docker compose down -v`).

```bash
curl http://localhost:8000/api/v1/health
```

Documentação interativa em `http://localhost:8000/docs`.

Pra derrubar tudo (incluindo o volume do banco):

```bash
docker compose down -v
```

## Rodando localmente sem Docker

Requer um Postgres acessível e um `.env` na raiz do projeto — a configuração **sempre** vem do `.env` (via `pydantic-settings`), nunca de um valor padrão no código. Sem ele, a aplicação (e os testes) falham já na importação, com um erro claro do Pydantic:

```bash
cp .env.example .env
# edite .env se sua string de conexão for diferente do padrão
```

Variáveis do `.env` (todas obrigatórias, sem valor padrão no código):

| Variável             | Descrição                                          |
| -------------------- | -------------------------------------------------- |
| `DATABASE_URL`       | String de conexão do Postgres.                     |
| `JWT_SECRET`         | Segredo de assinatura dos tokens (use 32+ bytes).  |
| `JWT_EXPIRE_MINUTES` | Validade do token de acesso, em minutos.           |
| `POSTGRES_*`         | Usuário, senha e banco usados pelo Docker Compose. |

```bash
uv sync
uv run fastapi dev src/recomendacoes_api/app.py
```

Isso cria um `.venv` local e instala todas as dependências travadas em `uv.lock`. O servidor sobe em `http://127.0.0.1:8000` com hot-reload habilitado.

Documentação interativa:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Rodando os testes

Requer um `.env` presente (`cp .env.example .env`), mesmo que os testes não toquem um banco real — `settings.py` é importado na cadeia de módulos e falha sem ele.

```bash
uv run pytest -v
```

Os testes são organizados por camada:

- `tests/domain/` — entidades testadas isoladamente, sem framework ou infraestrutura envolvida.
- `tests/application/` — use cases testados com repositórios mock, sem banco de dados ou servidor HTTP (inclui a matriz de permissões por papel).
- `tests/adapters/database/` — repositórios reais contra um SQLite em memória, mais os mocks (`Mock<Entidade>Repository`) reutilizados nas outras camadas.
- `tests/adapters/security/` — hash de senha (argon2) e tokens JWT, mais os mocks dessas portas.
- `tests/adapters/rest/` — endpoints testados via `TestClient`, com `dependency_overrides` para injetar use cases construídos com mocks.

## Lint e formatação

```bash
uv run ruff check .      # lint
uv run ruff format .     # formata o código
```

Configurado em `[tool.ruff]` no `pyproject.toml` (line length 100, regras de pyflakes/pycodestyle/isort/pyupgrade/bugbear).

## API

Todas as rotas ficam sob `/api/v1`. Rotas marcadas com 🔒 exigem `Authorization: Bearer <token>`. Listagens são paginadas com `limit` (1 a 100) e `offset`, e respondem `{"total": int, "items": [...]}`. Erros seguem o formato `{"error": "...", "code": 400, "message": "..."}`.

| Módulo       | Rotas                                                                                                                                   | Requisitos       |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Autenticação | `POST /auth/register`, `POST /auth/login`, 🔒 `GET /auth/me`                                                                            | RF01, RF02       |
| Viagens      | 🔒 `POST /trips`, `GET /trips` (painel, inclui compartilhadas), `GET/PUT/DELETE /trips/{id}`, `POST /trips/join`                        | RF04, RF05, RF06 |
| Destinos     | 🔒 `POST/GET /trips/{id}/destinations`, `PUT /trips/{id}/destinations/order`, `PUT/DELETE /trips/{id}/destinations/{destination_id}`    | RF08, RF09       |
| Atividades   | `GET /activities` e `GET /activities/{id}` (públicos), 🔒 `POST /activities`, 🔒 `/trips/{id}/destinations/{id}/activities` (agendar)   | RF12, RF13, RF14 |
| Orçamento    | 🔒 `PUT /trips/{id}/budget`; o custo previsto fica em cada atividade agendada                                                           | RF15, RF16       |
| Colaboração  | 🔒 `GET /trips/{id}/collaborators`, `PUT/DELETE /trips/{id}/collaborators/{user_id}`                                                    | RF18, RF19, RF20 |
| Avaliações   | 🔒 `PUT /activities/{id}/review`, `GET /activities/{id}/reviews` (público)                                                              | RF22, RF23       |

Como funciona a colaboração: cada viagem tem um `invite_code`, visível só para o criador. Quem o envia em `POST /trips/join` entra como **Visualizador**, e o criador pode promovê-lo a **Editor** ou removê-lo.

| Ação                                              | Criador | Editor | Visualizador | Não participante |
| ------------------------------------------------- | :-----: | :----: | :----------: | :--------------: |
| Ler viagem, destinos, atividades e colaboradores  |   ✅    |   ✅   |      ✅      |       403        |
| Editar destinos, atividades agendadas e orçamento |   ✅    |   ✅   |     403      |       403        |
| Editar/excluir a viagem, gerenciar colaboradores  |   ✅    |  403   |     403      |       403        |

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
| `domain/entities.py`             | Objetos de negócio centrais e seus invariantes (`User`, `Trip`, `Destination`, `Activity`, `Review`…). Python puro, sem imports de framework.                                                                 |
| `domain/exceptions.py`           | Exceções de negócio (ex: `InvalidTripError`), uma por tipo de erro, levantadas pelas entidades ou pelos use cases.                                                  |
| `ports/repositories.py`          | Interfaces (`Protocol`) que o domínio exige do mundo externo — ex: `TripRepository`. Portas não-repositório (`PasswordHasher`, `TokenService`) ficam em `ports/security.py`. Definidas para a aplicação, implementadas nos adapters.                        |
| `application/use_cases.py`       | Orquestra entidades e ports para cumprir um caso de uso específico (ex: `CreateTripUseCase`). Sem regra de negócio própria, sem código de framework.                 |
| `adapters/rest/`                 | **Driving adapter** — traduz requisições HTTP em chamadas de use case, objetos de domínio em respostas de API, e exceções de domínio em respostas HTTP de erro.      |
| `adapters/database/`             | **Driven adapter** — implementa as ports com um mecanismo concreto: Postgres via SQLAlchemy em `adapters/database/`, argon2 e JWT em `adapters/security/`.                                                        |
| `settings.py`                    | Configuração via variáveis de ambiente (`pydantic-settings`), ex: `DATABASE_URL`, `JWT_SECRET`.                                                                                     |

## Estrutura do projeto

```
src/recomendacoes_api/
├── app.py                       # Entrypoint do FastAPI (registra rotas, exception handlers, lifespan)
├── settings.py                  # Configuração via variáveis de ambiente
├── domain/
│   ├── entities.py              # User, Trip (agregado com colaboradores), Destination, Activity, Review…
│   ├── exceptions.py            # Exceções de negócio, uma por tipo de erro
│   └── pagination.py            # Page[T] compartilhado pelas listagens
├── ports/
│   ├── repositories.py          # Interfaces que a aplicação exige da persistência
│   └── security.py              # PasswordHasher e TokenService
├── application/
│   └── use_cases.py             # Um use case por ação (VerbNounUseCase.execute)
└── adapters/
    ├── rest/                    # Driving adapter: controllers, schemas, dependencies, exception handlers
    ├── database/                # Driven adapter: sessão SQLAlchemy + repositórios Postgres
    └── security/                # Driven adapter: Argon2PasswordHasher e JwtTokenService
```

## Docker

- `Dockerfile` — build multi-stage usando `uv` (instala dependências, depois copia o código).
- `docker-compose.yml` — orquestra a API e um Postgres padrão (`postgres:16-alpine`), com healthcheck garantindo que a API só sobe depois do banco estar pronto.
- `.dockerignore` — exclui `.venv`, `tests/`, caches e arquivos de editor da imagem.
