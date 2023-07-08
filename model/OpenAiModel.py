import transformers
from langchain.llms import HuggingFacePipeline
from torch import cuda, bfloat16
from langchain.chat_models import ChatOpenAI

class OpenAiModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = ChatOpenAI()#type: ignore
        return cls._instance

    @classmethod
    def get_model_pipeline(cls):
        return cls._instance

open_ai_model = OpenAiModel()