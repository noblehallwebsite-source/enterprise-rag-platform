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

def run_rag_pipeline(
    session_id: str,
    query: str,
    filters: dict = None
):

#     retrieved_docs = search_documents(
#         query=query,
#         top_k=3,
#         filters=filters
#     )
   
    conversation_history = get_conversation_history(
        session_id
    )

    # STEP 7: Build conversational history context block
    history_context = ""
    for message in conversation_history:
        history_context += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )


    # Core Pipeline: Broad Candidate Recall
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

    context = "\n".join([
        item["text"]
        for item in reranked_docs
    ])

# STEP 8: Fully updated prompt context combining past dialogue and current hits
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

    ai_answer = generate_ai_response(
        augmented_prompt
    )

    # STEP 9: Append current transaction turn into database persistent storage
    save_message(
        session_id=session_id,
        role="user",
        content=query
    )

    save_message(
        session_id=session_id,
        role="assistant",
        content=ai_answer
    )

    return {
        "query": query,
        "retrieved_context": reranked_docs,
        "ai_answer": ai_answer
    }