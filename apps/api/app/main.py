from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Enterprise AI Knowledge Assistant API",
    description="API for the Enterprise AI Knowledge Assistant",
    version="1.0.0",
)

# CORS Configuration
# In production, this should be restricted to the specific origins of the frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return HealthResponse(status="ok", message="API is healthy and running")

from app.api.v1.auth import router as auth_router
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
