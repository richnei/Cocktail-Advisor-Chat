import os
from decouple import config
from utils.data_processor import CocktailDataProcessor
from api.services.vector_store_service import VectorStoreService

# Configure environment variables
os.environ['OPENAI_API_KEY'] = config('OPENAI_API_KEY')

def initialize_database():
    """Initialize the vector database with cocktail data"""
    print("Initializing cocktail database...")

    # Process dataset
    data_processor = CocktailDataProcessor()
    documents = data_processor.process_dataset("data/cocktails.csv")

    print(f"Processed {len(documents)} cocktail documents")

    # Add to vector database
    vector_store = VectorStoreService()
    vector_store.add_documents(documents)

    print("Database initialization complete!")

if __name__ == "__main__":
    initialize_database()