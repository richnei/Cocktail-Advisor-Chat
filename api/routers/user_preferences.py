from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..services.vector_store_service import VectorStoreService

router = APIRouter()

class PreferenceRequest(BaseModel):
    preference_type: str  # e.g., "ingredients", "cocktails"
    content: List[str]

class PreferenceResponse(BaseModel):
    status: str
    stored_preferences: List[str]

def get_vector_store():
    return VectorStoreService()

@router.post("/preferences", response_model=PreferenceResponse)
async def store_preferences(
    request: PreferenceRequest,
    vector_store_service: VectorStoreService = Depends(get_vector_store)
):
    vector_store_service.store_user_preference(request.preference_type, request.content)

    # Retrieve stored preferences to confirm
    stored = vector_store_service.get_user_preferences(request.preference_type)

    return {
        "status": "success",
        "stored_preferences": stored
    }

@router.get("/preferences/{preference_type}", response_model=List[str])
async def get_preferences(
    preference_type: str,
    vector_store_service: VectorStoreService = Depends(get_vector_store)
):
    preferences = vector_store_service.get_user_preferences(preference_type)
    return preferences

@router.get("/debug/preferences", response_model=dict)
async def debug_preferences(
    vector_store_service: VectorStoreService = Depends(get_vector_store)
):
    all_preferences = {
        "ingredients": vector_store_service.get_user_preferences("ingredients"),
        "cocktails": vector_store_service.get_user_preferences("cocktails")
    }
    return all_preferences