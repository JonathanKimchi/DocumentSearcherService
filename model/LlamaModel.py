import transformers
from langchain.llms import HuggingFacePipeline, LlamaCpp
from torch import cuda, bfloat16
from model.BaseModel import BaseModel
from langchain.llms import TextGen

from llama_cpp import Llama

n_gpu_layers = 81  # Change this value based on your model and your GPU VRAM pool.
n_batch = 512  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

class LlamaModel(BaseModel):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.llm = TextGen(model_url="http://localhost:5000")
            cls._instance.tokenizer = transformers.AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")#type: ignore

        return cls._instance

    @classmethod
    def get_model_pipeline(cls):
        return cls()._instance.llm#type: ignore

# llama_model = LlamaModel()