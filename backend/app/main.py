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

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Enterprise RAG Platform",
    version="1.0.0"
)

# Your origins configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://ai.noblehall.com",
]

# The middleware assignment block
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

app.include_router(document_router)
app.include_router(rag_router)
app.include_router(chat_routes.router, prefix="/api")


@app.get("/")
def root():

    return {
        "message": "Enterprise RAG Platform Running Correctly"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }