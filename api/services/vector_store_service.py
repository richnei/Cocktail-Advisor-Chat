import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

class VectorStoreService:
    def __init__(self, persist_directory='db'):
        self.persist_directory = persist_directory
        self.embedding_function = OpenAIEmbeddings()
        self.vector_store = self._load_or_create_vector_store()

    def _load_or_create_vector_store(self):
        if os.path.exists(os.path.join(self.persist_directory)):
            return Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function,
            )
        return None

    def add_documents(self, documents):
        if self.vector_store:
            self.vector_store.add_documents(documents)
        else:
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_function,
                persist_directory=self.persist_directory,
            )
        return self.vector_store

    def get_retriever(self):
        if self.vector_store:
            return self.vector_store.as_retriever()
        return None

    def search_similar(self, query, k=5):
        if self.vector_store:
            return self.vector_store.similarity_search(query, k=k)
        return []

    def store_user_preference(self, preference_type, content):
        """Store user preferences in the vector store"""
        if not self.vector_store:
            self.vector_store = self._load_or_create_vector_store()
            if not self.vector_store:
                # If we don't have a vector store yet, create an empty one
                self.vector_store = Chroma.from_documents(
                    documents=[],
                    embedding=self.embedding_function,
                    persist_directory=self.persist_directory,
                )
                print("Creating new vector store for preferences")

        # Create a document for each preference
        from langchain_core.documents import Document

        # Convert content list to string (ChromaDB doesn't accept lists as values)
        content_str = ", ".join(content)

        # Check if a preference document already exists
        existing_docs = self.vector_store.get(
            where={"preference_type": preference_type}
        )

        if existing_docs and len(existing_docs['documents']) > 0:
            # Get existing preferences as string
            existing_content_str = existing_docs['metadatas'][0].get('content_str', "")

            # Convert back to list, add new items and remove duplicates
            existing_content = existing_content_str.split(", ") if existing_content_str else []
            updated_content = list(set(existing_content + content))

            # Convert back to string
            updated_content_str = ", ".join(updated_content)

            # Remove existing document
            self.vector_store.delete(
                where={"preference_type": preference_type}
            )

            # Update content string
            content_str = updated_content_str

        # Create document
        doc = Document(
            page_content=f"User preference - {preference_type}: {content_str}",
            metadata={
                "preference_type": preference_type,
                "content_str": content_str,  # Store as string
                "source": "user_preference"
            }
        )

        # Add to vector store
        self.vector_store.add_documents([doc])
        return True

    def get_user_preferences(self, preference_type):
        """Get user preferences from the vector store"""
        if not self.vector_store:
            return []

        # Fetch preferences
        results = self.vector_store.get(
            where={"preference_type": preference_type}
        )

        if results and len(results['documents']) > 0:
            # Get preference string and convert to list
            content_str = results['metadatas'][0].get('content_str', "")
            if content_str:
                return content_str.split(", ")

        return []