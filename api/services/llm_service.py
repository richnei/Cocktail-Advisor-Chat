from langchain_openai import ChatOpenAI

class LLMService:
    def __init__(self, model_name="gpt-3.5-turbo"):
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name)

    def get_llm(self):
        return self.llm

    def set_model(self, model_name):
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name)