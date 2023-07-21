import transformers
from langchain.llms import HuggingFacePipeline, LlamaCpp
from torch import cuda, bfloat16
from model.BaseModel import BaseModel

from llama_cpp import Llama

class LlamaModel(BaseModel):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.llm = LlamaCpp(model_path='model_data/llama-2-13b-chat.ggmlv3.q2_K.bin', n_ctx=1000, n_batch=8, callbacks=[], verbose=False)

            cls._instance.tokenizer = transformers.AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")#type: ignore

            # cls._instance.generate_text = transformers.pipeline(#type: ignore
            #     model=cls._instance.model, tokenizer=cls._instance.tokenizer,#type: ignore
            #     return_full_text=True,  # langchain expects the full text
            #     task='text-generation',
            #     # we pass model parameters here too
            #     device=cls._instance.device,#type: ignore
            #     temperature=0.1,  # 'randomness' of outputs, 0.0 is the min and 1.0 the max
            #     top_p=0.15,  # select from top tokens whose probability add up to 15%
            #     top_k=0,  # select from top 0 tokens (because zero, relies on top_p)
            #     max_new_tokens=64,  # mex number of tokens to generate in the output
            #     repetition_penalty=1.1  # without this output begins repeating
            # )
        return cls._instance

    @classmethod
    def get_model_pipeline(cls):
        return cls()._instance.llm#HuggingFacePipeline(pipeline=cls()._instance.generate_text)#type: ignore

llama_model = LlamaModel()