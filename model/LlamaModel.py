import transformers
from langchain.llms import HuggingFacePipeline, LlamaCpp
from torch import cuda, bfloat16
from model.BaseModel import BaseModel

from llama_cpp import Llama

n_gpu_layers = 40  # Change this value based on your model and your GPU VRAM pool.
n_batch = 512  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

class LlamaModel(BaseModel):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.llm = LlamaCpp(
                model_path='model_data/llama-2-13b-chat.ggmlv3.q2_K.bin', 
                n_ctx=3000, 
                n_gpu_layers=n_gpu_layers,
                n_batch=n_batch,
                callbacks=[], 
                verbose=False)
            cls._instance.tokenizer = transformers.AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")#type: ignore

        return cls._instance

    @classmethod
    def get_model_pipeline(cls):
        return cls()._instance.llm#type: ignore

llama_model = LlamaModel()