from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..services.rag_service import RAGService
from ..services.llm_service import LLMService
from ..services.vector_store_service import VectorStoreService

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    chat_history: Optional[List[Message]] = None
    model: Optional[str] = "gpt-3.5-turbo"

class ChatResponse(BaseModel):
    answer: str

class RecommendationRequest(BaseModel):
    criteria: str
    count: Optional[int] = 5

def get_rag_service():
    llm_service = LLMService()
    vector_store_service = VectorStoreService()
    return RAGService(llm_service, vector_store_service)

def get_vector_store_service():
    return VectorStoreService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, rag_service: RAGService = Depends(get_rag_service)):
    # Configure model if specified
    rag_service.llm_service.set_model(request.model)

    # Process chat history
    chat_history = request.chat_history if request.chat_history else []

    # Get response
    response = rag_service.ask_question(request.query, chat_history)

    return {"answer": response.get("answer", "No answer found")}

@router.get("/preferences")
async def get_preferences(vector_store_service: VectorStoreService = Depends(get_vector_store_service)):
    """Returns the user's saved preferences"""
    try:
        # Fetch ingredient preferences
        preferences = vector_store_service.get_user_preferences("ingredients")
        return {"preferences": preferences}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching preferences: {str(e)}")

@router.post("/recommend", response_model=dict)
async def recommend_cocktails(
    request: RecommendationRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Recommends cocktails based on criteria or saved preferences"""
    try:
        recommendations = rag_service.recommend_cocktails(request.criteria, request.count)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recommending cocktails: {str(e)}")