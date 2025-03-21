import pandas as pd
from langchain_core.documents import Document

class CocktailDataProcessor:
    def __init__(self):
        pass

    def load_cocktails_data(self, file_path):
        """Load cocktails data from CSV file"""
        df = pd.read_csv(file_path)
        return df

    def convert_to_documents(self, df):
        """Convert DataFrame to Langchain documents"""
        documents = []

        for _, row in df.iterrows():
            # Extract relevant information
            name = row.get('name', '')
            ingredients = row.get('ingredients', '')
            instructions = row.get('instructions', '')

            # Create document content
            content = f"Cocktail: {name}\nIngredients: {ingredients}\nInstructions: {instructions}"

            # Create metadata
            metadata = {
                'name': name,
                'ingredients': ingredients,
                'source': 'cocktails_dataset'
            }

            # Create document
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)

        return documents

    def process_dataset(self, file_path):
        """Process cocktail dataset and return documents"""
        df = self.load_cocktails_data(file_path)
        documents = self.convert_to_documents(df)
        return documents