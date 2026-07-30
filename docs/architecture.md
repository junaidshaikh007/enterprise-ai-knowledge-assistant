# Enterprise AI Knowledge Assistant - Architecture

## Overview
The Enterprise AI Knowledge Assistant is a multi-tenant RAG (Retrieval-Augmented Generation) application designed for enterprise document management and Q&A.

## Components
1. **Frontend (Next.js):** Provides a responsive web interface for document uploads, management, and chat interactions. Uses Tailwind CSS and shadcn/ui.
2. **Backend (FastAPI):** Handles API requests, orchestration, and business logic.
3. **Database (PostgreSQL):** Stores relational data (users, organizations, document metadata, chat history). Accessed asynchronously via SQLAlchemy.
4. **Vector Store (Qdrant):** Stores document chunks and their semantic embeddings.
5. **Cache/Message Broker (Redis):** Caches frequent responses and acts as a broker for background tasks.
6. **Background Worker (Celery):** Processes document ingestion, text extraction, chunking, and embedding asynchronously.
7. **Object Storage (MinIO):** Stores original uploaded document files securely.

## Data Flow
- **Ingestion:** User uploads a document -> API saves to MinIO -> API creates a Celery task -> Worker downloads from MinIO, extracts text, chunks, embeds, and stores in Qdrant -> Updates PostgreSQL with metadata.
- **Retrieval & Q&A:** User asks a question -> API generates query embedding -> Qdrant performs hybrid search -> API retrieves context -> LLM generates grounded answer with citations -> Frontend streams response.

## Chat Streaming Contract
`POST /api/v1/chat/` returns a `text/event-stream` response. Each event contains a JSON payload:

- `sources`: emitted first with the retrieved document chunks in `{ "sources": [...] }`.
- `token`: emitted once for each generated text fragment in `{ "token": "..." }`.
- `done`: emitted once after generation completes as `{ "done": true }`.

Clients should append `token` values in order, render the source metadata when it arrives, and finish the active response after `done`.

## RAG Pipeline
- Utilizes LlamaIndex for orchestration.
- Dense (semantic) and Sparse (keyword) retrieval combined with Hybrid Fusion.
- Strict multi-tenancy enforced at the database and vector store query level.
