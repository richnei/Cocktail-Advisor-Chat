from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

class RAGService:
    def __init__(self, llm_service, vector_store_service):
        self.llm_service = llm_service
        self.vector_store_service = vector_store_service

    def ask_question(self, query, chat_history=None):
        llm = self.llm_service.get_llm()
        retriever = self.vector_store_service.get_retriever()

        if not retriever:
            return {"answer": "No cocktail data available. Please load the dataset first."}

        system_prompt = """
        You are a cocktail expert and advisor. Use the provided context to answer questions about cocktails.
        If the information is not in the context, say you don't have that information.
        If the user mentions their favorite ingredients, remember them for future recommendations.

        Context: {context}
        """

        messages = [("system", system_prompt)]
        if chat_history:
            for message in chat_history:
                # Check if message is a dictionary or an object
                if hasattr(message, 'role') and hasattr(message, 'content'):
                    # If it's an object with role and content attributes
                    messages.append((message.role, message.content))
                elif isinstance(message, dict):
                    # If it's a dictionary
                    messages.append((message.get("role"), message.get("content")))
                else:
                    # If it's neither of the expected formats, skip
                    continue

        messages.append(("human", "{input}"))

        prompt = ChatPromptTemplate.from_messages(messages)

        question_answer_chain = create_stuff_documents_chain(
            llm=llm,
            prompt=prompt,
        )

        chain = create_retrieval_chain(
            retriever=retriever,
            combine_docs_chain=question_answer_chain,
        )

        response = chain.invoke({"input": query})

        # Detect user preferences
        self._detect_user_preferences(query)

        return response

    def recommend_cocktails(self, criteria, count=5):
        """Recommend cocktails based on criteria"""
        llm = self.llm_service.get_llm()
        retriever = self.vector_store_service.get_retriever()

        if not retriever:
            return {"recommendations": [], "message": "No cocktail data available."}

        # Check if we're searching based on favorite ingredients
        if "favorite" in criteria.lower() or "favourite" in criteria.lower():
            favorite_ingredients = self.vector_store_service.get_user_preferences("ingredients")

            if not favorite_ingredients:
                return {"recommendations": [], "message": "No favorite ingredients found. Please tell me what ingredients you like first."}

            # Build query with favorite ingredients
            ingredients_text = ", ".join(favorite_ingredients)
            search_query = f"cocktails with {ingredients_text}"
        else:
            # Use criteria directly
            search_query = criteria

        # Search for similar documents
        similar_docs = self.vector_store_service.search_similar(search_query, k=count)

        # Extract recommendations from documents
        recommendations = []
        for doc in similar_docs:
            cocktail_name = doc.metadata.get("name", "Unknown cocktail")
            if cocktail_name not in [rec.get("name") for rec in recommendations]:
                recommendations.append({
                    "name": cocktail_name,
                    "ingredients": doc.metadata.get("ingredients", ""),
                    "content": doc.page_content
                })

        return {
            "recommendations": recommendations[:count],
            "message": f"Here are {len(recommendations[:count])} cocktail recommendations based on {search_query}"
        }

    def _detect_user_preferences(self, query):
        """Detect user preferences from the query"""
        # Keywords that indicate preferences
        favorite_keywords = [
            "favorite", "favourite", "love", "like", "prefer", "enjoy"
        ]

        query_lower = query.lower()
        print(f"Detecting preferences in: {query_lower}")  # Debug log

        # Check if the query contains preference keywords
        if any(keyword in query_lower for keyword in favorite_keywords):
            print("Preference keyword detected")  # Debug log
            # List of common ingredients to detect
            common_ingredients = [
                "rum", "vodka", "gin", "tequila", "whiskey", "bourbon",
                "brandy", "cognac", "lime", "lemon", "orange", "mint",
                "sugar", "syrup", "juice", "soda", "tonic", "vermouth",
                "bitters", "grenadine", "cream", "coffee", "chocolate"
            ]

            # Find mentioned ingredients
            found_ingredients = []
            for ingredient in common_ingredients:
                if ingredient in query_lower:
                    found_ingredients.append(ingredient)
                    print(f"Ingredient found: {ingredient}")  # Debug log

            # If ingredients were found, store them
            if found_ingredients:
                print(f"Storing preferences: {found_ingredients}")  # Debug log
                success = self.vector_store_service.store_user_preference("ingredients", found_ingredients)
                print(f"Storage successful: {success}")  # Debug log
                return True
            else:
                print("No known ingredients found")  # Debug log

        return False