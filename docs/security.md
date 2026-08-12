# Enterprise AI Knowledge Assistant - Security Architecture

## Multi-Tenancy Isolation
Every organization operates in strict isolation. 
- **Database:** All queries to PostgreSQL must filter by `organization_id`.
- **Vector Store:** Qdrant collections use payload filters to strictly segment vectors by `organization_id`.
- **Storage:** MinIO object paths use the `organization_id` as the root prefix.

## Authentication & Authorization
- Uses JWT-based authentication.
- Passwords are hashed using bcrypt.
- **Roles:** Owner, Admin, Member, Viewer. Each role has specific permissions enforced at the API route level.

## Data Protection
- **Prompt Injection Defense:** Strict constraints in LLM system prompts. Retrieved context is clearly separated from instructions using delimiters.
- No execution of instructions found within uploaded documents.
- Internal stack traces are never exposed to the frontend.

## API Security
- Strict CORS rules restricting origins.
- Rate limiting implemented via Redis.
- File-size and MIME-type validation for all uploads. Safe file-name handling using sanitized UUIDs.
- Environment variables hold all secrets. No API keys or secrets committed to Git.

## Tenant Isolation Audit (Day 28)
- Chat requests validate an optional chat session against both the authenticated user and `organization_id` before storing messages.
- Session deletion and message history use tenant- and user-scoped session checks; history queries also join through the owned session.
- Document listing, status, and deletion scope their database queries to the authenticated user and `organization_id`.
- Vector retrieval filters Qdrant results by `organization_id` supplied only from the authenticated organization dependency.
- Routes return `404 Not Found` for inaccessible sessions and documents, avoiding disclosure of cross-tenant resource existence.
