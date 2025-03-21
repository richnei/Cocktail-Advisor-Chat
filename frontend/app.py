import streamlit as st
import requests

# API Configuration
API_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title='Cocktail Advisor Chat',
    page_icon='🍹',
)

st.header('🍹 Cocktail Advisor Chat')

# Sidebar for information
with st.sidebar:
    st.header('About')
    st.write("This is a cocktail advisor chat that can answer questions about cocktails and provide recommendations based on your preferences.")
    st.write("Try asking about cocktails, mentioning your favorite ingredients, or requesting recommendations!")

    # Preference management section
    st.sidebar.subheader("Preferences")

    # Show preferences button
    if st.sidebar.button("Show My Preferences"):
        try:
            prefs_response = requests.get(f"{API_URL}/preferences")
            preferences_data = prefs_response.json()

            if preferences_data and "preferences" in preferences_data and preferences_data["preferences"]:
                preferences = preferences_data["preferences"]

                st.sidebar.subheader("Your Favorite Ingredients")

                # Display each ingredient with an emoji
                for ingredient in preferences:
                    # Emojis for common ingredients
                    emoji_map = {
                        "vodka": "🥃",
                        "rum": "🥃",
                        "gin": "🍸",
                        "tequila": "🥃",
                        "whiskey": "🥃",
                        "bourbon": "🥃",
                        "lemon": "🍋",
                        "lime": "🍋",
                        "orange": "🍊",
                        "mint": "🌿",
                        "sugar": "🧂",
                        "syrup": "🍯",
                        "juice": "🧃",
                        "coffee": "☕",
                        "chocolate": "🍫",
                        "cream": "🥛",
                        "soda": "🥤",
                        "tonic": "💧",
                        "bitters": "💧",
                        "grenadine": "🍒",
                        "vermouth": "🍷"
                    }

                    # Get emoji or use a default
                    emoji = emoji_map.get(ingredient.lower(), "🍹")

                    # Display with proper capitalization
                    st.sidebar.write(f"{emoji} {ingredient.capitalize()}")
            else:
                st.sidebar.info("No favorite ingredients yet. Try telling the chatbot what you like!")

        except Exception as e:
            st.sidebar.error(f"Error fetching preferences: {str(e)}")

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("Ask about cocktails...")

if prompt:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare request for API
    chat_history = st.session_state.messages[:-1]  # Exclude current message

    payload = {
        "query": prompt,
        "chat_history": chat_history,
        "model": "gpt-3.5-turbo"  # Fixed model
    }

    # Make API request
    with st.spinner("Thinking..."):
        try:
            response = requests.post(f"{API_URL}/chat", json=payload)
            response.raise_for_status()
            answer = response.json().get("answer", "Sorry, I couldn't process your request.")
        except Exception as e:
            answer = f"Error communicating with the API: {str(e)}"

    # Display response
    with st.chat_message("assistant"):
        st.markdown(answer)

    # Add response to history
    st.session_state.messages.append({"role": "assistant", "content": answer})