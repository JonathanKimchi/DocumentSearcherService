import transformers
from langchain.llms import HuggingFacePipeline
from torch import cuda, bfloat16
from langchain.chat_models import ChatOpenAI
from model.BaseModel import BaseModel

class OpenAiModel(BaseModel):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model_pipeline = ChatOpenAI(temperature=0.25)#type: ignore
        return cls._instance

    @classmethod
    def get_model_pipeline(cls):
        return cls._instance.model_pipeline#type: ignore

open_ai_model = OpenAiModel()