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



# import time
# # from app.services.chroma_service import (
# #     search_documents
# # )

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

# # Fast API Streaming Import
# from fastapi.responses import StreamingResponse

# # Centralized Prometheus operational metrics instrumentation
# from app.services.metrics_service import (
#     rag_requests_total,
#     rag_failures_total,
#     rag_latency_seconds,
#     retrieved_documents_total
# )

# # Evaluation service module import
# from app.services.evaluation_service import (
#     evaluate_grounding
# )

# # =====================================================================
# # UPDATED: STREAM GENERATOR WITH BACKGROUND MEMORY & EVALUATION
# # =====================================================================
# # Added reranked_docs to the function parameters
# def stream_llm_response(client, augmented_prompt, session_id, query, reranked_docs):
#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {
#                 "role": "system",
#                 "content": "You are an enterprise infrastructure AI assistant."
#             },
#             {
#                 "role": "user",
#                 "content": augmented_prompt
#             }
#         ],
#         stream=True
#     )

#     full_response_text = ""
    
#     # 1. Process token chunks incrementally live from Groq (Fast UI response)
#     for chunk in response:
#         if chunk.choices and chunk.choices[0].delta.content:
#             delta = chunk.choices[0].delta.content
#             full_response_text += delta
#             yield delta

#     # -----------------------------------------------------------------
#     # THE STREAM HAS ENDED: Execute background operations safely
#     # -----------------------------------------------------------------
#     try:
#         # 2. Run Grounding Evaluation on the completed text string
#         evaluation_result = evaluate_grounding(
#             answer=full_response_text,
#             retrieved_documents=reranked_docs
#         )
        
#         # Log it to your terminal/container stdout for verification
#         print(f"\n[EVALUATION] Session: {session_id} | Result: {evaluation_result}")
        
#         # MLOps Pro-Tip: You can expand this line later to save evaluation_result 
#         # to your persistent database alongside logs for tracking drift/hallucinations!
        
#     except Exception as eval_error:
#         print(f"\n[EVALUATION FAILURE] Could not evaluate grounding: {eval_error}")

#     # 3. Save the completed conversational turn to history database
#     save_message(
#         session_id=session_id,
#         role="user",
#         content=query
#     )
#     save_message(
#         session_id=session_id,
#         role="assistant",
#         content=full_response_text
#     )


# # =====================================================================
# # EXISTING BLOCKING RAG PIPELINE (WITH METRICS & EVALUATION)
# # =====================================================================
# def run_rag_pipeline(
#     session_id: str,
#     query: str,
#     filters: dict = None
# ):
#     rag_requests_total.inc()
#     start_time = time.time()

#     try:
#         conversation_history = get_conversation_history(session_id)

#         history_context = ""
#         for message in conversation_history:
#             history_context += f"{message['role']}: {message['content']}\n"

#         retrieved_docs = hybrid_search(query=query, top_k=10, filters=filters)
#         reranked_docs = rerank_documents(query=query, documents=retrieved_docs, top_k=3)
        
#         retrieved_documents_total.observe(len(reranked_docs))

#         context = "\n".join([item["text"] for item in reranked_docs])

#         augmented_prompt = f"""
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

#         ai_answer = generate_ai_response(augmented_prompt)

#         evaluation_result = evaluate_grounding(
#             answer=ai_answer,
#             retrieved_documents=reranked_docs
#         )

#         save_message(session_id=session_id, role="user", content=query)
#         save_message(session_id=session_id, role="assistant", content=ai_answer)

#         total_latency = time.time() - start_time
#         rag_latency_seconds.observe(total_latency)

#         return {
#             "query": query,
#             "retrieved_context": reranked_docs,
#             "ai_answer": ai_answer,
#             "evaluation": evaluation_result
#         }

#     except Exception as e:
#         rag_failures_total.inc()
#         raise e


# # =====================================================================
# # UPDATED: STREAMING RAG PIPELINE
# # =====================================================================
# def run_streaming_rag_pipeline(
#     client,
#     session_id: str,
#     query: str,
#     filters: dict = None
# ):
#     rag_requests_total.inc()
#     start_time = time.time()

#     try:
#         conversation_history = get_conversation_history(session_id)

#         history_context = ""
#         for message in conversation_history:
#             history_context += f"{message['role']}: {message['content']}\n"

#         retrieved_docs = hybrid_search(
#             query=query,
#             top_k=10,
#             filters=filters
#         )

#         reranked_docs = rerank_documents(
#             query=query,
#             documents=retrieved_docs,
#             top_k=3
#         )

#         retrieved_documents_total.observe(len(reranked_docs))

#         context = "\n".join([
#             item["text"]
#             for item in reranked_docs
#         ])

#         augmented_prompt = f"""
# You are an enterprise infrastructure AI assistant.

# Conversation History:
# {history_context}

# Retrieved Infrastructure Context:
# {context}

# Current User Question:
# {query}

# Provide a direct, comprehensive engineering markdown response based on the context.
# """

#         total_latency = time.time() - start_time
#         rag_latency_seconds.observe(total_latency)

#         # Pass your reranked_docs context list down into the streaming payload generator
#         return StreamingResponse(
#             stream_llm_response(
#                 client=client,
#                 augmented_prompt=augmented_prompt,
#                 session_id=session_id,
#                 query=query,
#                 reranked_docs=reranked_docs  # 🔥 Added parameter passing here
#             ),
#             media_type="text/plain"
#         )

#     except Exception as e:
#         rag_failures_total.inc()
#         raise e



# import time
# # from app.services.chroma_service import (
# #     search_documents
# # )

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

# # Fast API Streaming Import
# from fastapi.responses import StreamingResponse

# # Centralized Prometheus operational metrics instrumentation
# from app.services.metrics_service import (
#     rag_requests_total,
#     rag_failures_total,
#     rag_latency_seconds,
#     retrieved_documents_total
# )

# # Evaluation service module import
# from app.services.evaluation_service import (
#     evaluate_grounding
# )


# # =====================================================================
# # NEW: ISOLATED ASYNC BACKGROUND WORKER TASK
# # =====================================================================
# def perform_background_evaluation_and_memory(full_response_text: dict, reranked_docs: list, session_id: str, query: str):
#     """
#     Runs safely in a separate thread managed by FastAPI after the token stream ends.
#     """
#     actual_text = full_response_text.get("text", "")
#     print(f"\n[BACKGROUND] Starting evaluation/memory sequence for session: {session_id}")
    
#     if not actual_text:
#         print("[BACKGROUND FAILURE] Generated text buffer was empty. Skipping sequence.")
#         return

#     try:
#         # 1. Run Grounding Evaluation on the final text string
#         evaluation_result = evaluate_grounding(
#             answer=actual_text,
#             retrieved_documents=reranked_docs
#         )
#         print(f"[EVALUATION SUCCESS] Session: {session_id} | Result: {evaluation_result}")
#     except Exception as eval_error:
#         print(f"[EVALUATION FAILURE] Could not evaluate grounding: {eval_error}")

#     try:
#         # 2. Save Conversational Turn to History
#         save_message(session_id=session_id, role="user", content=query)
#         save_message(session_id=session_id, role="assistant", content=actual_text)
#         print(f"[MEMORY SUCCESS] Chat history appended for session: {session_id}")
#     except Exception as mem_error:
#         print(f"[MEMORY FAILURE] Could not save message: {mem_error}")


# # =====================================================================
# # CLEAN CHUNK STREAM GENERATOR
# # =====================================================================
# def stream_llm_response(client, augmented_prompt, shared_buffer: dict):
#     response = client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[
#             {
#                 "role": "system",
#                 "content": "You are an enterprise infrastructure AI assistant."
#             },
#             {
#                 "role": "user",
#                 "content": augmented_prompt
#             }
#         ],
#         stream=True
#     )

#     full_response_text = ""
#     for chunk in response:
#         if chunk.choices and chunk.choices[0].delta.content:
#             delta = chunk.choices[0].delta.content
#             full_response_text += delta
#             yield delta

#     # Store the complete text in the shared dictionary reference so the background worker task can read it
#     shared_buffer["text"] = full_response_text


# # =====================================================================
# # EXISTING BLOCKING RAG PIPELINE (RESTORED & WITH EVALUATION)
# # =====================================================================
# def run_rag_pipeline(
#     session_id: str,
#     query: str,
#     filters: dict = None
# ):
#     rag_requests_total.inc()
#     start_time = time.time()

#     try:
#         conversation_history = get_conversation_history(session_id)

#         history_context = ""
#         for message in conversation_history:
#             history_context += f"{message['role']}: {message['content']}\n"

#         retrieved_docs = hybrid_search(query=query, top_k=10, filters=filters)
#         reranked_docs = rerank_documents(query=query, documents=retrieved_docs, top_k=3)
        
#         retrieved_documents_total.observe(len(reranked_docs))

#         context = "\n".join([item["text"] for item in reranked_docs])

#         augmented_prompt = f"""
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

#         ai_answer = generate_ai_response(augmented_prompt)

#         evaluation_result = evaluate_grounding(
#             answer=ai_answer,
#             retrieved_documents=reranked_docs
#         )

#         save_message(session_id=session_id, role="user", content=query)
#         save_message(session_id=session_id, role="assistant", content=ai_answer)

#         total_latency = time.time() - start_time
#         rag_latency_seconds.observe(total_latency)

#         return {
#             "query": query,
#             "retrieved_context": reranked_docs,
#             "ai_answer": ai_answer,
#             "evaluation": evaluation_result
#         }

#     except Exception as e:
#         rag_failures_total.inc()
#         raise e


# # =====================================================================
# # UPDATED: STREAMING RAG PIPELINE
# # =====================================================================
# def run_streaming_rag_pipeline(
#     client,
#     session_id: str,
#     query: str,
#     background_tasks,  # Handled by FastAPI BackgroundTask loop worker threads
#     filters: dict = None
# ):
#     rag_requests_total.inc()
#     start_time = time.time()

#     try:
#         conversation_history = get_conversation_history(session_id)

#         history_context = ""
#         for message in conversation_history:
#             history_context += f"{message['role']}: {message['content']}\n"

#         retrieved_docs = hybrid_search(
#             query=query,
#             top_k=10,
#             filters=filters
#         )

#         reranked_docs = rerank_documents(
#             query=query,
#             documents=retrieved_docs,
#             top_k=3
#         )

#         retrieved_documents_total.observe(len(reranked_docs))

#         context = "\n".join([
#             item["text"]
#             for item in reranked_docs
#         ])

#         augmented_prompt = f"""
# You are an enterprise infrastructure AI assistant.

# Conversation History:
# {history_context}

# Retrieved Infrastructure Context:
# {context}

# Current User Question:
# {query}

# Provide a direct, comprehensive engineering markdown response based on the context.
# """

#         total_latency = time.time() - start_time
#         rag_latency_seconds.observe(total_latency)

#         # Shared dictionary object to pass strings out from generator safely by reference
#         shared_buffer = {"text": ""}

#         # Add the background worker tracking payload task
#         background_tasks.add_task(
#             perform_background_evaluation_and_memory,
#             full_response_text=shared_buffer,
#             reranked_docs=reranked_docs,
#             session_id=session_id,
#             query=query
#         )

#         return StreamingResponse(
#             stream_llm_response(
#                 client=client,
#                 augmented_prompt=augmented_prompt,
#                 shared_buffer=shared_buffer
#             ),
#             media_type="text/plain"
#         )

#     except Exception as e:
#         rag_failures_total.inc()
#         raise e

import time

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

# FastAPI Streaming Import
from fastapi.responses import StreamingResponse

# Centralized Prometheus operational metrics instrumentation
from app.services.metrics_service import (
    rag_requests_total,
    rag_failures_total,
    rag_latency_seconds,
    retrieved_documents_total
)

# Evaluation service module import
from app.services.evaluation_service import (
    evaluate_grounding
)


# =====================================================================
# TENANT-AWARE BACKGROUND WORKER TASK
# =====================================================================
def perform_background_evaluation_and_memory(
    tenant_id: str,        # 🔥 Pass tenant id down for isolated context
    full_response_text: dict, 
    reranked_docs: list, 
    session_id: str, 
    query: str
):
    """
    Runs safely in a separate thread managed by FastAPI after the token stream ends.
    Insulates memory storage by matching the active tenant scope.
    """
    actual_text = full_response_text.get("text", "")
    print(f"\n[BACKGROUND] Starting evaluation/memory sequence for tenant: {tenant_id} | session: {session_id}")
    
    if not actual_text:
        print("[BACKGROUND FAILURE] Generated text buffer was empty. Skipping sequence.")
        return

    try:
        # 1. Run Grounding Evaluation on the final text string
        evaluation_result = evaluate_grounding(
            answer=actual_text,
            retrieved_documents=reranked_docs
        )
        print(f"[EVALUATION SUCCESS] Session: {session_id} | Result: {evaluation_result}")
    except Exception as eval_error:
        print(f"[EVALUATION FAILURE] Could not evaluate grounding: {eval_error}")

    try:
        # 2. Save Conversational Turn to History (Ensure your memory layer supports tenant namespaces)
        save_message(session_id=session_id, role="user", content=query)
        save_message(session_id=session_id, role="assistant", content=actual_text)
        print(f"[MEMORY SUCCESS] Chat history appended for session: {session_id}")
    except Exception as mem_error:
        print(f"[MEMORY FAILURE] Could not save message: {mem_error}")


# =====================================================================
# CLEAN CHUNK STREAM GENERATOR
# =====================================================================
def stream_llm_response(client, augmented_prompt, shared_buffer: dict):
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
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            delta = chunk.choices[0].delta.content
            full_response_text += delta
            yield delta

    # Store the complete text in the shared dictionary reference so the background worker task can read it
    shared_buffer["text"] = full_response_text


# =====================================================================
# TENANT-ISOLATED BLOCKING RAG PIPELINE
# =====================================================================
def run_rag_pipeline(
    tenant_id: str,        # 🔥 Required tenant parameter
    session_id: str,
    query: str,
    filters: dict = None
):
    rag_requests_total.inc()
    start_time = time.time()

    try:
        conversation_history = get_conversation_history(session_id)

        history_context = ""
        for message in conversation_history:
            history_context += f"{message['role']}: {message['content']}\n"

        # Pass tenant id directly down to scope the knowledge base query
        retrieved_docs = hybrid_search(tenant_id=tenant_id, query=query, top_k=10, filters=filters)
        reranked_docs = rerank_documents(query=query, documents=retrieved_docs, top_k=3)
        
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

        evaluation_result = evaluate_grounding(
            answer=ai_answer,
            retrieved_documents=reranked_docs
        )

        save_message(session_id=session_id, role="user", content=query)
        save_message(session_id=session_id, role="assistant", content=ai_answer)

        total_latency = time.time() - start_time
        rag_latency_seconds.observe(total_latency)

        return {
            "query": query,
            "retrieved_context": reranked_docs,
            "ai_answer": ai_answer,
            "evaluation": evaluation_result
        }

    except Exception as e:
        rag_failures_total.inc()
        raise e


# =====================================================================
# TENANT-ISOLATED STREAMING RAG PIPELINE
# =====================================================================
def run_streaming_rag_pipeline(
    client,
    tenant_id: str,        # 🔥 Required tenant parameter
    session_id: str,
    query: str,
    background_tasks,  
    filters: dict = None
):
    rag_requests_total.inc()
    start_time = time.time()

    try:
        conversation_history = get_conversation_history(session_id)

        history_context = ""
        for message in conversation_history:
            history_context += f"{message['role']}: {message['content']}\n"

        # Pass tenant id directly down to hybrid search
        retrieved_docs = hybrid_search(
            tenant_id=tenant_id,
            query=query,
            top_k=10,
            filters=filters
        )

        reranked_docs = rerank_documents(
            query=query,
            documents=retrieved_docs,
            top_k=3
        )

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

Provide a direct, comprehensive engineering markdown response based on the context.
"""

        total_latency = time.time() - start_time
        rag_latency_seconds.observe(total_latency)

        shared_buffer = {"text": ""}

        # Pass tenant id down to the managed async worker task queue loop
        background_tasks.add_task(
            perform_background_evaluation_and_memory,
            tenant_id=tenant_id,
            full_response_text=shared_buffer,
            reranked_docs=reranked_docs,
            session_id=session_id,
            query=query
        )

        return StreamingResponse(
            stream_llm_response(
                client=client,
                augmented_prompt=augmented_prompt,
                shared_buffer=shared_buffer
            ),
            media_type="text/plain"
        )

    except Exception as e:
        rag_failures_total.inc()
        raise e