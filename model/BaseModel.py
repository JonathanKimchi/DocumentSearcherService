import transformers
from langchain.llms import HuggingFacePipeline
from torch import cuda, bfloat16

class BaseModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)#type: ignore
        return cls._instance

    @classmethod
    def get_model_pipeline(cls):
        return cls._instance