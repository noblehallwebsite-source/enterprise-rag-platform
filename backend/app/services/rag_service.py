# from app.services.chroma_service import (
#     search_documents
# )

# from app.services.hybrid_search_service import (
#     hybrid_search
# )

# from app.services.ai_service import (
#     generate_ai_response
# )

# from app.services.rerank_service import (
#     rerank_documents
# )

# from app.services.memory_service import (
#     save_message,
#     get_conversation_history
# )

# from fastapi.responses import StreamingResponse

# def run_rag_pipeline(
#     session_id: str,
#     query: str,
#     filters: dict = None
# ):



# #     retrieved_docs = search_documents(
# #         query=query,
# #         top_k=3,
# #         filters=filters
# #     )
   
#     conversation_history = get_conversation_history(
#         session_id
#     )

#     # STEP 7: Build conversational history context block
#     history_context = ""
#     for message in conversation_history:
#         history_context += (
#             f"{message['role']}: "
#             f"{message['content']}\n"
#         )


#     # Core Pipeline: Broad Candidate Recall
#     retrieved_docs = hybrid_search(
#         query=query,
#         top_k=10,
#         filters=filters
#     )

#     reranked_docs = rerank_documents(
#         query=query,
#         documents=retrieved_docs,
#         top_k=3
#     )

#     context = "\n".join([
#         item["text"]
#         for item in reranked_docs
#     ])

# # STEP 8: Fully updated prompt context combining past dialogue and current hits
#     augmented_prompt = f"""
# You are an enterprise infrastructure AI assistant.

# Conversation History:
# {history_context}

# Retrieved Infrastructure Context:
# {context}

# Current User Question:
# {query}

# Return a JSON response with the keys:
# "answer": the final response text
# "documents": list of documents used
# "conversation_updated": true or false
# "next_followup_suggestions": 2–3 ideas for follow-up questions
# "critical_infrastructure_issue": true/false (detected security or availability risk)"""

#     ai_answer = generate_ai_response(
#         augmented_prompt
#     )

#     # STEP 9: Append current transaction turn into database persistent storage
#     save_message(
#         session_id=session_id,
#         role="user",
#         content=query
#     )

#     save_message(
#         session_id=session_id,
#         role="assistant",
#         content=ai_answer
#     )

#     return {
#         "query": query,
#         "retrieved_context": reranked_docs,
#         "ai_answer": ai_answer
#     }



import time
# from app.services.chroma_service import (
#     search_documents
# )

from app.services.hybrid_search_service import (
    hybrid_search
)

from app.services.ai_service import (
    generate_ai_response
)

from app.services.rerank_service import (
    rerank_documents
)

from app.services.memory_service import (
    save_message,
    get_conversation_history
)

# Fast API Streaming Import
from fastapi.responses import StreamingResponse

# STEP 3: Centralized Prometheus operational metrics instrumentation
from app.services.metrics_service import (
    rag_requests_total,
    rag_failures_total,
    rag_latency_seconds,
    retrieved_documents_total
)

# =====================================================================
# STREAM GENERATOR WITH BACKGROUND MEMORY PERSISTENCE
# =====================================================================
def stream_llm_response(client, augmented_prompt, session_id, query):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are an enterprise infrastructure AI assistant."
            },
            {
                "role": "user",
                "content": augmented_prompt
            }
        ],
        stream=True
    )

    full_response_text = ""
    
    # Process token chunks incrementally live from Groq
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            delta = chunk.choices[0].delta.content
            full_response_text += delta
            yield delta

    # Once streaming concludes, save the turn to history
    save_message(
        session_id=session_id,
        role="user",
        content=query
    )
    save_message(
        session_id=session_id,
        role="assistant",
        content=full_response_text
    )


# =====================================================================
# EXISTING BLOCKING RAG PIPELINE (WITH METRICS)
# =====================================================================
def run_rag_pipeline(
    session_id: str,
    query: str,
    filters: dict = None
):
    # STEP 4 & 7: Track requests entrypoint and capture potential failures
    rag_requests_total.inc()
    start_time = time.time()

    try:
        conversation_history = get_conversation_history(session_id)

        history_context = ""
        for message in conversation_history:
            history_context += f"{message['role']}: {message['content']}\n"

        retrieved_docs = hybrid_search(query=query, top_k=10, filters=filters)
        reranked_docs = rerank_documents(query=query, documents=retrieved_docs, top_k=3)
        
        # STEP 5: Track how many docs successfully made it past the reranking filter
        retrieved_documents_total.observe(len(reranked_docs))

        context = "\n".join([item["text"] for item in reranked_docs])

        augmented_prompt = f"""
You are an enterprise infrastructure AI assistant.

Conversation History:
{history_context}

Retrieved Infrastructure Context:
{context}

Current User Question:
{query}

Return a JSON response with the keys:
"answer": the final response text
"documents": list of documents used
"conversation_updated": true or false
"next_followup_suggestions": 2–3 ideas for follow-up questions
"critical_infrastructure_issue": true/false (detected security or availability risk)"""

        ai_answer = generate_ai_response(augmented_prompt)

        save_message(session_id=session_id, role="user", content=query)
        save_message(session_id=session_id, role="assistant", content=ai_answer)

        # STEP 6: Calculate total structural execution latency before returning
        total_latency = time.time() - start_time
        rag_latency_seconds.observe(total_latency)

        return {
            "query": query,
            "retrieved_context": reranked_docs,
            "ai_answer": ai_answer
        }

    except Exception as e:
        # STEP 7: Increment failures counter on errors
        rag_failures_total.inc()
        raise e


# =====================================================================
# NEW STREAMING RAG PIPELINE (WITH METRICS)
# =====================================================================
def run_streaming_rag_pipeline(
    client,
    session_id: str,
    query: str,
    filters: dict = None
):
    # STEP 4 & 7: Initialize instrumentation tracking hooks
    rag_requests_total.inc()
    start_time = time.time()

    try:
        # Keep history loading exactly as before
        conversation_history = get_conversation_history(session_id)

        history_context = ""
        for message in conversation_history:
            history_context += f"{message['role']}: {message['content']}\n"

        # Keep retrieval, hybrid search, and reranking exactly as before
        retrieved_docs = hybrid_search(
            query=query,
            top_k=10,
            filters=filters
        )

        reranked_docs = rerank_documents(
            query=query,
            documents=retrieved_docs,
            top_k=3
        )

        # STEP 5: Track retrieval document observation volume
        retrieved_documents_total.observe(len(reranked_docs))

        context = "\n".join([
            item["text"]
            for item in reranked_docs
        ])

        # Construct clean prompt for real-time text layout
        augmented_prompt = f"""
You are an enterprise infrastructure AI assistant.

Conversation History:
{history_context}

Retrieved Infrastructure Context:
{context}

Current User Question:
{query}

Provide a direct, comprehensive engineering markdown response based on the context.
"""

        # STEP 6: Capture TTSR (Time to Stream Response) heavy lifting block latency
        total_latency = time.time() - start_time
        rag_latency_seconds.observe(total_latency)

        # Replace final response with real-time text/plain stream
        return StreamingResponse(
            stream_llm_response(
                client=client,
                augmented_prompt=augmented_prompt,
                session_id=session_id,
                query=query
            ),
            media_type="text/plain"
        )

    except Exception as e:
        # STEP 7: Track system crash logs natively inside Prometheus metrics
        rag_failures_total.inc()
        raise e