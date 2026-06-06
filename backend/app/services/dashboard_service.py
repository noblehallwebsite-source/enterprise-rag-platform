import httpx
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.chat_session import ChatSession
from app.models.message import Message

# Target the internal Docker network alias we defined in docker-compose
PROMETHEUS_URL = "http://enterprise-rag-prometheus:9090/api/v1/query"

def query_prometheus_metric(query_expr: str) -> float:
    """
    Dedicated Infrastructure Telemetry Layer:
    Queries the persistent Prometheus TSDB container engine using PromQL.
    """
    try:
        response = httpx.get(PROMETHEUS_URL, params={"query": query_expr}, timeout=2.0)
        if response.status_code == 200:
            data = response.json()
            results = data.get("data", {}).get("result", [])
            if results:
                # Prometheus values are returned as strings like ["1717711200", "42"]
                return float(results[0]["value"][1])
    except Exception as e:
        print(f"Prometheus Connection Alert: {e}")
    return 0.0

def get_tenant_dashboard_metrics(db: Session, tenant_id: str) -> dict:
    """
    Application Layer Analytics Assembler:
    Executes precise structural counts across core system relational entities
    scoped to a single tenant partition boundary, augmented with long-term 
    telemetry pulled directly from the Prometheus TSDB via query_prometheus_metric.
    """
    
    # 1. Base Relational Database Counts (Postgres Disk Persistence)
    document_count = db.query(Document).filter(Document.tenant_id == tenant_id).count()
    session_count = db.query(ChatSession).filter(ChatSession.tenant_id == tenant_id).count()
    message_count = db.query(Message).join(ChatSession, Message.session_id == ChatSession.id).filter(ChatSession.tenant_id == tenant_id).count()

    # 2. Extract Persistent Custom Counters from Prometheus TSDB via PromQL
    total_requests = query_prometheus_metric("rag_requests_total")
    total_failures = query_prometheus_metric("rag_failures_total")
    
    # Defensive programming for success matrix
    success_rate = 100.0
    if total_requests > 0:
        success_rate = round(((total_requests - total_failures) / total_requests) * 100, 1)

    # 3. Calculate True Average API Latency over the last 5 minutes using the Histogram metric
    # We take the 5-minute rate of the latency sum and divide it by the 5-minute rate of the count
    latency_query = "sum(rate(rag_latency_seconds_sum[5m])) / sum(rate(rag_latency_seconds_count[5m]))"
    avg_latency = round(query_prometheus_metric(latency_query), 2)

    return {
        "documents": document_count,
        "chat_sessions": session_count,
        "messages": message_count,
        "tenants": 1,
        "success_rate": success_rate,
        "avg_latency": avg_latency,
        "total_requests": int(total_requests)
    }