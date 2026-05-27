from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="Enterprise RAG Platform",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)

@app.get("/")
def root():
    return {
        "message": "Enterprise RAG Platform Running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }