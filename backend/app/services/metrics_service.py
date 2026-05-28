from prometheus_client import Counter
from prometheus_client import Histogram


# =========================
# Request Counters
# =========================

rag_requests_total = Counter(
    "rag_requests_total",
    "Total number of RAG requests"
)

rag_failures_total = Counter(
    "rag_failures_total",
    "Total number of failed RAG requests"
)

# =========================
# Retrieval Metrics
# =========================

retrieved_documents_total = Histogram(
    "retrieved_documents_total",
    "Number of retrieved documents"
)

# =========================
# Latency Metrics
# =========================

rag_latency_seconds = Histogram(
    "rag_latency_seconds",
    "RAG request latency"
)