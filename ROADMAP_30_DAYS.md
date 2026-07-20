# 30-Part Daily Commit Plan (Phases 6–10)

This roadmap breaks down the remaining work (Phases 6 to 10) into **30 daily micro-steps**. Each part is designed to be completed in one day and committed with a clean commit message.

---

### 🟡 Section 1: Frontend Chat Interface (Days 1–7)
* **[x] Day 1**: Scaffold the main chat page layout (`apps/web/src/app/chat/page.tsx`) with a sidebar and message window.
  * *Commit:* `feat: scaffold main chat page layout`
* **[ ] Day 2**: Build the chat sidebar UI listing active/past chat sessions with hover effects and a "New Chat" button.
  * *Commit:* `feat: implement chat sidebar UI`
* **[ ] Day 3**: Implement the message input container at the bottom of the chat window (auto-resizing text area, send button, Enter-to-submit).
  * *Commit:* `feat: create chat input text area component`
* **[ ] Day 4**: Design the user and assistant message bubbles (`ChatMessage.tsx`) supporting avatars and distinct background styles.
  * *Commit:* `feat: implement message bubble rendering components`
* **[ ] Day 5**: Add rich text and basic Markdown rendering to the message bubble content.
  * *Commit:* `feat: add markdown rendering to chat messages`
* **[ ] Day 6**: Build the collapsible source references panel below assistant bubbles to display document names and retrieval confidence scores.
  * *Commit:* `feat: implement source reference citations panel`
* **[ ] Day 7**: Connect the frontend chat interface to the `/api/v1/chat` endpoint using React state.
  * *Commit:* `feat: integrate chat UI with non-streaming chat endpoint`

---

### ⚪ Section 2: Response Streaming via SSE (Days 8–12)
* **[ ] Day 8**: Update the backend `llm_service.py` to yield tokens asynchronously from OpenAI's API.
  * *Commit:* `feat: modify llm service to yield tokens asynchronously`
* **[ ] Day 9**: Upgrade the `/api/v1/chat` POST route to return a FastAPI `StreamingResponse` using Server-Sent Events (SSE).
  * *Commit:* `feat: implement server-sent events for chat endpoint`
* **[ ] Day 10**: Create a python validation script in `scratch/` to test and print the stream output.
  * *Commit:* `test: add helper script to verify sse stream output`
* **[ ] Day 11**: Write a custom React hook/utility in the frontend to process chunked SSE streams using `ReadableStream`.
  * *Commit:* `feat: implement frontend readable stream reader for sse`
* **[ ] Day 12**: Wire the SSE streaming reader into the Next.js chat page to show tokens rendering in real-time.
  * *Commit:* `feat: connect chat UI to streaming response stream`

---

### ⚪ Section 3: Conversation Memory & Database History (Days 13–18)
* **[ ] Day 13**: Define SQLAlchemy models for `ChatSession` and `ChatMessage` with tenant foreign key relations.
  * *Commit:* `feat: create database models for chat sessions and history`
* **[ ] Day 14**: Autogenerate and apply Alembic migrations for the new chat tables.
  * *Commit:* `chore: run migrations for chat history tables`
* **[ ] Day 15**: Create API endpoints to create, fetch, and delete chat sessions.
  * *Commit:* `feat: build api endpoints for chat sessions`
* **[ ] Day 16**: Create API endpoint to load messages for a specific session.
  * *Commit:* `feat: build api endpoint to fetch session message history`
* **[ ] Day 17**: Update the `/chat` controller to save new questions and answers in PostgreSQL dynamically.
  * *Commit:* `feat: persist conversations to database on chat completion`
* **[ ] Day 18**: Connect the Next.js sidebar and load chat histories dynamically when a session is selected.
  * *Commit:* `feat: integrate database chat history in frontend sidebar`

---

### ⚪ Section 4: Asynchronous Processing via Celery & Redis (Days 19–25)
* **[ ] Day 19**: Add Redis image to Docker Compose and add `celery` + `redis` dependencies to requirements.
  * *Commit:* `chore: configure redis container and backend celery dependencies`
* **[ ] Day 20**: Initialize the Celery application (`celery_app.py`) and setup worker configurations.
  * *Commit:* `chore: initialize celery application instance`
* **[ ] Day 21**: Migrate document parsing, chunking, and embedding logic into a background Celery task.
  * *Commit:* `feat: create document ingestion celery task`
* **[ ] Day 22**: Add a processing status tracking field (`PENDING`, `PROCESSING`, `SUCCESS`, `FAILED`) to the document database model.
  * *Commit:* `feat: add status field and tracker to document models`
* **[ ] Day 23**: Update the `/upload` API endpoint to register the document in DB and trigger the Celery task asynchronously.
  * *Commit:* `feat: make document upload API asynchronous via task queue`
* **[ ] Day 24**: Create a document status checking endpoint (`/documents/{doc_id}/status`) to verify completion.
  * *Commit:* `feat: add api endpoint to poll document ingestion status`
* **[ ] Day 25**: Implement visual upload progress and processing states in Next.js by polling the status API.
  * *Commit:* `feat: add ingestion progress indicator to dashboard UI`

---

### ⚪ Section 5: Observability, Evaluation & Deployment (Days 26–30)
* **[ ] Day 26**: Integrate the Langfuse SDK to log and trace vector searches and LLM prompt/response pairs.
  * *Commit:* `feat: integrate langfuse observability and tracing`
* **[ ] Day 27**: Write automated DeepEval tests to evaluate faithfulness and answer relevance.
  * *Commit:* `test: add deepeval test cases for rag pipelines`
* **[ ] Day 28**: Audit all endpoints to ensure strict tenant validation on `organization_id`.
  * *Commit:* `security: audit multi-tenant request isolation`
* **[ ] Day 29**: Create production-grade Dockerfiles for frontend, backend, and workers.
  * *Commit:* `chore: write multi-stage production dockerfiles`
* **[ ] Day 30**: Complete local end-to-end builds, documentation cleanup, and manual verification.
  * *Commit:* `chore: finalize setup, polish README, and verify build`
