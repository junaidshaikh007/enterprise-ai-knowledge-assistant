# Local Verification

Run these checks from the repository root after installing the API and web dependencies.

## Automated checks

```powershell
.\scripts\verify-api.ps1
.\scripts\verify-web.ps1
```

The API check runs its regression suite. The web check runs ESLint and creates a production Next.js build.

## Manual end-to-end check

1. Start the API, frontend, PostgreSQL, Qdrant, Redis, and Celery worker with the required environment settings.
2. Register a new organization and sign in.
3. Upload a PDF, TXT, or DOCX file and wait for its status to become `SUCCESS`.
4. Ask a question about that document and confirm that the response streams with source references.
5. Start a new chat, reopen an existing chat, and confirm its history is preserved.
