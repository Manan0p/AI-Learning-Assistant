# AI Learning Assistant

> **Live API:** [https://learningassist-sev.vercel.app/docs](https://learningassist-sev.vercel.app/docs)

A production-ready AI-powered backend that generates personalized learning roadmaps, recommends portfolio projects, and answers learner questions through a full retrieval-augmented generation (RAG) pipeline — built with FastAPI, PostgreSQL + pgvector, Redis, and Google Gemini.

---

## Overview

Most learning platforms give every user the same static curriculum. This service takes a different approach: it asks for your goal, your experience level, and what you already know — then it generates a structured, week-by-week roadmap tailored specifically to you, embeds it into a vector store, and answers your follow-up questions by retrieving only the most relevant context from your own roadmap. No hallucinated generic advice — only grounded, personalized guidance.

### What it does

| Feature | Description |
|---|---|
| **Roadmap Generation** | Produces a structured, multi-phase learning roadmap with weekly milestones calibrated to the learner's experience and goal. |
| **Portfolio Project Recommendations** | Generates one concrete, achievable portfolio project tied to a roadmap or a set of target skills. |
| **RAG Chat** | Embeds the learner's question, retrieves the top 5 relevant roadmap chunks by cosine similarity, and answers using only that retrieved context. |
| **Progress Tracking** | Tracks per-phase completion state (`pending` → `in_progress` → `completed`) across roadmaps. |
| **Response Caching** | Caches Gemini generation responses in Redis to avoid redundant LLM calls for identical inputs. |
| **Health Monitoring** | Exposes a health endpoint that checks database and Redis connectivity independently. |

---

## Live Demo

The interactive API documentation (Swagger UI) is available at:

```
https://learningassist-sev.vercel.app/docs
```

All endpoints are fully explorable and executable from the browser. No authentication required.

---

## Architecture

The application is fully asynchronous and organized strictly by responsibility layer, with no cross-layer imports from outer to inner:

```
app/
├── api/          # FastAPI route handlers and dependency injection wiring
├── core/         # Settings, structured logging (Loguru), and exception hierarchy
├── db/           # SQLAlchemy async engine and session factory
├── models/       # SQLAlchemy 2.0 ORM models (roadmaps, chunks, projects, chat, progress)
├── schemas/      # Pydantic v2 request/response models and LLM output schemas
├── repositories/ # Database access layer — all raw queries live here
├── services/     # Business logic: Gemini, embeddings, RAG, caching, health
├── prompts/      # Prompt templates (separated from service logic)
└── utils/        # JSON extraction and markdown rendering helpers
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12 |
| Web Framework | FastAPI with async-native routing |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.0 async |
| Database | PostgreSQL 16 with pgvector extension |
| Migrations | Alembic |
| LLM | Google Gemini 2.5 Flash |
| Embeddings | Google `gemini-embedding-2` (768 dimensions) |
| Vector Search | pgvector with HNSW index and cosine similarity |
| Caching | Redis (opportunistic — failures are non-breaking) |
| Text Chunking | LangChain `RecursiveCharacterTextSplitter` (chunking utility only) |
| Logging | Loguru structured logging |
| Containerization | Docker + Docker Compose |
| Code Quality | Ruff, Black, mypy, Pytest |

---

## API Endpoints

Base path: `/api/v1`

### `POST /roadmap`
Accepts the learner's goal, experience level, and known skills. Generates a validated JSON roadmap, persists it, converts it to markdown, chunks it semantically, embeds each chunk with `gemini-embedding-2`, and stores the vectors in pgvector — all in a single request.

### `POST /project`
Generates one concrete, achievable portfolio project. Accepts either a `roadmap_id` (to derive context from an existing roadmap) or a direct `goal_title` + `skills` pair.

### `POST /chat`
Implements the full RAG pipeline: embeds the user's question using retrieval-query mode, retrieves the top 5 roadmap chunks by cosine distance from pgvector, builds a compact context prompt, generates a grounded answer with Gemini 2.5 Flash, and persists both the chat turn and the retrieved chunk IDs for traceability.

### `GET /progress?roadmap_id=...`
Returns all progress items for a roadmap along with the overall completion percentage.

### `PATCH /progress`
Updates a single progress item. Accepted states: `pending`, `in_progress`, `completed`.

### `GET /api/v1/health`
Returns independent status checks for the database and Redis connections. Used for uptime monitoring.

---

## RAG Pipeline Design

The `/chat` endpoint does not inject the entire roadmap into the prompt. It follows a strict retrieval workflow:

1. Embed the user query with `gemini-embedding-2` in `RETRIEVAL_QUERY` mode.
2. Search `roadmap_chunks` for the top 5 chunks ordered by pgvector cosine distance.
3. Build a compact prompt containing only those retrieved chunks — no padding.
4. Generate a JSON response with Gemini 2.5 Flash, instructed to answer only from the provided context and to explicitly admit when context is insufficient.
5. Persist the chat turn along with the retrieved chunk IDs for traceability and future analytics.

---

## Chunking Strategy

Roadmaps are converted to markdown before chunking because headings, bullet points, milestones, and weekly plans create semantically useful boundaries. The chunker targets approximately 400 tokens by using 1,600 characters per chunk with a 300-character overlap (~75-token overlap). This keeps each chunk focused on a single phase or milestone while preserving continuity across boundaries.

---

## Prompt Engineering

- All prompts require **JSON-only output** with no markdown fences — reducing the need for post-processing.
- Each generation prompt includes the **exact Pydantic JSON schema** so the model knows the precise output contract.
- The roadmap prompt emphasizes realistic weekly cadence, measurable milestones, and portfolio orientation.
- The project prompt targets a single specific, achievable project — not a list of ideas.
- The chat prompt strictly instructs Gemini to answer only from retrieved context and to acknowledge missing information rather than improvise.
- Malformed LLM output is parsed defensively and **retried up to 3 times with exponential backoff**.
- Transient Gemini 503/429 errors are caught separately and also retried, returning a clear upstream-failure message to the caller instead of a generic server error.

---

## Database Schema

### `roadmaps`
Stores the learner's input (goal, experience, skills), the validated roadmap JSON, a markdown rendering, and timestamps.

### `roadmap_chunks`
Stores chunk text and a `vector(768)` embedding generated by `gemini-embedding-2`. Indexed with HNSW using `vector_cosine_ops` for fast approximate nearest-neighbour retrieval.

### `projects`
Stores generated portfolio project JSON with optional linkage to a parent roadmap.

### `chat_messages`
Stores user and assistant turns, follow-up question suggestions, and the IDs of the chunks retrieved for each response.

### `progress_items`
Stores per-phase completion state for each roadmap.

---

## Local Development

### Using Docker (recommended)

```bash
cp .env.example .env
# Set GOOGLE_API_KEY in .env
docker compose up --build
```

API docs will be available at `http://localhost:8000/docs`.

The container runs Alembic migrations automatically on startup.

### Using Poetry

```bash
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

### Using pip

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\Activate.ps1         # Windows PowerShell
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

---

## Quality Checks

```bash
ruff check .
black --check .
mypy app
pytest
```

---

## Deployment

Deployed on **Vercel** with:
- **Neon** — managed PostgreSQL 16 with pgvector (pooled connection)
- **Upstash** — serverless Redis for response caching

Environment variables required:

| Variable | Description |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...?ssl=require` (Neon pooled URL) |
| `REDIS_URL` | `redis://default:...` (Upstash URL) |
| `GOOGLE_API_KEY` | Google AI Studio API key |
| `GEMINI_MODEL` | e.g. `gemini-2.5-flash` or `gemini-2.0-flash` |
| `EMBEDDING_MODEL` | `gemini-embedding-2` |

---

## Assumptions

- `gemini-embedding-2` embeddings are 768-dimensional vectors.
- A progress item maps to each generated roadmap phase.
- Redis caching is opportunistic: cache failures are logged at debug level and do not break core generation.
- Integration tests avoid live PostgreSQL, Redis, and Google calls — production behavior is validated through service boundaries and mocks.

---

## Use of AI Coding Assistants

This project was developed with the assistance of Codex and Antigravity (Google DeepMind). The assistants were primarily used for:

- Planning and producing an implementation plan.
- Accelerating boilerplate setup for FastAPI and SQLAlchemy 2.0 async patterns.
- Assisting in the implementation of the RAG pipeline with pgvector.
- Troubleshooting Docker and Vercel deployment configurations.

All architectural decisions, prompt engineering design, and final code reviews were directed and verified manually.

---

## Approximate Time Spent

| Phase | Time |
|---|---|
| Planning & Architecture | 30 min |
| API & Database Implementation | 45 min |
| AI Integration & RAG Pipeline | 45 min |
| Testing & Polish | 60 min |
| **Total** | **~3 hours** |

---

## Future Improvements

- Add user accounts and JWT-based authorization.
- Add streaming chat responses via Server-Sent Events.
- Add citation snippets inline in chat responses linking back to source chunks.
- Add full end-to-end tests with Testcontainers.
- Add background job queue for embedding large roadmaps asynchronously.
- Add analytics for roadmap completion rates and weak-skill detection.

---

## License

This project is licensed under the [MIT License](LICENSE).

