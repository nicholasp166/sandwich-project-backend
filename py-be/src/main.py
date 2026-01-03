from fastapi import FastAPI
from src.api.v1 import psbroute   # import your route modules

app = FastAPI(title="Document Converter API")

# Attach routers under /api/v1
app.include_router(psbroute.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
