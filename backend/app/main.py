# # app/main.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from prometheus_fastapi_instrumentator import Instrumentator

# # ... your existing imports ...
# from prometheus_client import generate_latest, CONTENT_TYPE_LATEST  # ← ADD THESE
# from fastapi import Response  # ← ADD THIS


# # Explicitly import all router layers cleanly
# from app.routes.document_routes import router as document_router
# from app.routes.rag_routes import router as rag_router
# from app.routes.chat_routes import router as chat_router
# from app.routes.dashboard_routes import router as dashboard_router  # 👈 Added the missing dashboard import
# from app.database.init_db import init_database  # 👈 Import your routine directly

# # Run your initialization sequence immediately on app context load
# init_database()

# app = FastAPI(
#     title="Enterprise RAG Platform",
#     version="1.0.0"
# )

# # Cross-Origin Resource Sharing (CORS) Configuration Policy
# origins = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "https://ai.noblehall.com",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize Prometheus Application Metric Telemetry Instrumentation Layer
# Instrumentator().instrument(app).expose(app)

# # Mount Routers under consistent architectural API endpoints
# app.include_router(document_router)
# app.include_router(rag_router)
# app.include_router(chat_router)
# app.include_router(dashboard_router)


# @app.get("/")
# def root():
#     return {
#         "message": "Enterprise RAG Platform Running Correctly"
#     }


# @app.get("/health")
# def health():
#     return {
#         "status": "healthy"
#     }

# # 👇 Expose the /metrics endpoint for Prometheus scraping tools
# @app.get("/metrics")
# def metrics():
#     return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

# Explicitly import all router layers cleanly
from app.routes.document_routes import router as document_router
from app.routes.rag_routes import router as rag_router
from app.routes.chat_routes import router as chat_router
from app.routes.dashboard_routes import router as dashboard_router
from app.database.init_db import init_database

# Run your initialization sequence immediately on app context load
init_database()

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

# 🚀 INITIALIZE & EXPOSE TELEMETRY
# This instruments the app AND handles the /metrics endpoint seamlessly, 
# exposing both default traffic metrics and your custom rag_* service metrics.
Instrumentator().instrument(app).expose(app)

# Mount Routers under consistent architectural API endpoints
app.include_router(document_router)
app.include_router(rag_router)
app.include_router(chat_router)
app.include_router(dashboard_router)


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


