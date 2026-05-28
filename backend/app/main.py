from fastapi import FastAPI

from prometheus_fastapi_instrumentator import (
    Instrumentator
)

from app.routes.document_routes import (
    router as document_router
)

from app.routes.rag_routes import (
    router as rag_router
)

app = FastAPI(
    title="Enterprise RAG Platform",
    version="1.0.0"
)

Instrumentator().instrument(app).expose(app)

app.include_router(document_router)
app.include_router(rag_router)


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