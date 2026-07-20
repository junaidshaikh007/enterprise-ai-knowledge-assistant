# Enterprise AI Knowledge Assistant - 10-Phase Roadmap

This document serves as the single source of truth for the development phases of the **Enterprise AI Knowledge Assistant** monorepo.

---

## 🟢 Phase 1: Project Initialization & Scaffold (Completed)
- **Goal:** Set up base repo, environments, Docker services, and framework skeletons.
- **Deliverables:**
  - Monorepo folder layout (`apps/web` for Next.js, `apps/api` for FastAPI, `infrastructure` for Docker, `docs`, `evaluation`).
  - Root docker-compose configuration for PostgreSQL, Qdrant, Redis, etc.
  - Foundational FastAPI app with CORS, logging, and `/health` monitoring.
  - Foundational Next.js app with Tailwind CSS and TypeScript.

## 🟢 Phase 2: Database & Multi-Tenant Authentication (Completed)
- **Goal:** Establish multi-tenant user authentication and PostgreSQL schema.
- **Deliverables:**
  - PostgreSQL models for `Organization` (Tenant) and `User` using UUIDs.
  - Alembic database migration pipeline.
  - Password hashing (bcrypt) and JWT token utilities.
  - API routes for `/login` and `/register` (creating both organizations and users).
  - Next.js signup, login, and redirection flows.

## 🟢 Phase 3: Document Processing & Ingestion (Completed)
- **Goal:** Enable file reading, text extraction, and text chunking.
- **Deliverables:**
  - Utilities to parse PDF, DOCX, and TXT files (`pypdf`, `python-docx`).
  - LangChain `RecursiveCharacterTextSplitter` configured for semantic chunking.
  - Next.js drag-and-drop frontend upload component and dashboard layout.
  - `/upload` API endpoint that receives files and extracts chunks in real-time.

## 🟢 Phase 4: Embeddings & Vector Store Integration (Completed)
- **Goal:** Set up semantic database storage and generate vectors.
- **Deliverables:**
  - Qdrant collection creation on startup.
  - OpenAI `text-embedding-3-small` integration.
  - Vector storage logic tagging chunks with `organization_id` for multi-tenant isolation.
  - Unified pipeline connecting `/upload` directly to vector ingestion.

## 🟢 Phase 5: Semantic Retrieval & Chat API (Completed)
- **Goal:** Core RAG pipeline construction (Retrieval + Generation).
- **Deliverables:**
  - Context Retrieval Service querying Qdrant with tenant payload filtering.
  - LLM Service using `gpt-4o` with strict instruction-based prompt templates.
  - `/api/v1/chat` POST endpoint orchestrating context retrieval and LLM response.

---

## 🟡 Phase 6: Frontend Chat Interface (Next Up)
- **Goal:** Build the frontend client interface for active conversations.
- **Deliverables:**
  - Next.js chat console page with history sidebar and active main conversation view.
  - Message bubble rendering components supporting markdown and citations.
  - API integration to fetch responses from `/api/v1/chat`.

## ⚪ Phase 7: Streaming Responses (SSE)
- **Goal:** Upgrade the chat experience to support token-by-token response streaming.
- **Deliverables:**
  - Upgrade FastAPI `/chat` endpoint to return a Server-Sent Events (SSE) streaming response.
  - Adjust frontend chat console to parse chunked SSE tokens and render text dynamically.

## ⚪ Phase 8: Conversational Memory & Database History
- **Goal:** Persist conversations and session listings for users.
- **Deliverables:**
  - PostgreSQL schemas for `ChatSession` and `ChatMessage` models.
  - Alembic migrations for history tracking.
  - Backend endpoints to retrieve session lists and load history.
  - Next.js sidebar integration displaying historical chats.

## ⚪ Phase 9: Background Ingestion via Celery & Redis
- **Goal:** Move resource-heavy parsing and embedding tasks out of the request-response cycle.
- **Deliverables:**
  - Setup Celery worker with Redis broker in root docker-compose.
  - Convert file uploads to dispatch background worker tasks.
  - Maintain document status field (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`) in database.

## ⚪ Phase 10: Observability, Evaluation & Production Polish
- **Goal:** Add enterprise tracing, quality benchmarks, and deployment assets.
- **Deliverables:**
  - Integration of Langfuse/DeepEval to log and evaluate generation quality.
  - Production-grade Dockerfiles for apps/web and apps/api.
  - Security audit on multi-tenancy filters and final production testing.
