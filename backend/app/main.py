# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

# Explicitly import all router layers cleanly
from app.routes.document_routes import router as document_router
from app.routes.rag_routes import router as rag_router
from app.routes.chat_routes import router as chat_router

app = FastAPI(
    title="Enterprise RAG Platform",
    version="1.0.0"
)

# Cross-Origin Resource Sharing (CORS) Configuration Policy
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://ai.noblehall.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Prometheus Application Metric Telemetry Instrumentation Layer
Instrumentator().instrument(app).expose(app)

# Mount Routers under consistent architectural API endpoints
app.include_router(document_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


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