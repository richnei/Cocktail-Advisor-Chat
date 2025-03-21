from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from decouple import config

from .routers import chat, user_preferences  # Remova cocktails daqui
from .services.vector_store_service import VectorStoreService

# Configure environment variables
os.environ['OPENAI_API_KEY'] = config('OPENAI_API_KEY')

app = FastAPI(title="Cocktail Advisor API")

# Configure CORS to allow requests from Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the Streamlit origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
# Remova esta linha:
# app.include_router(cocktails.router, prefix="/api", tags=["cocktails"])
app.include_router(user_preferences.router, prefix="/api", tags=["preferences"])

@app.get("/")
async def root():
    return {"message": "Welcome to Cocktail Advisor API"}

# Test endpoint for preferences
@app.get("/test-preferences")
async def test_preferences():
    vector_store_service = VectorStoreService()
    # Store test preferences (vodka and lemon)
    success = vector_store_service.store_user_preference("ingredients", ["vodka", "lemon"])
    prefs = vector_store_service.get_user_preferences("ingredients")
    return {"success": success, "preferences": prefs}