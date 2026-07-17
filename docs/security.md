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
