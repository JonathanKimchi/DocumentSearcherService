import transformers
from langchain.llms import HuggingFacePipeline
from torch import cuda, bfloat16

class LocalModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'#type: ignore
            cls._instance.model = transformers.AutoModelForCausalLM.from_pretrained(#type: ignore
                'mosaicml/mpt-7b-instruct',
                torch_dtype=bfloat16,
                trust_remote_code=True,
                max_seq_len=2048
            )
            cls._instance.model.eval()#type: ignore
            cls._instance.model.to(cls._instance.device)#type: ignore

            cls._instance.tokenizer = transformers.AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")#type: ignore

            cls._instance.generate_text = transformers.pipeline(#type: ignore
                model=cls._instance.model, tokenizer=cls._instance.tokenizer,#type: ignore
                return_full_text=True,  # langchain expects the full text
                task='text-generation',
                # we pass model parameters here too
                device=cls._instance.device,#type: ignore
                temperature=0.1,  # 'randomness' of outputs, 0.0 is the min and 1.0 the max
                top_p=0.15,  # select from top tokens whose probability add up to 15%
                top_k=0,  # select from top 0 tokens (because zero, relies on top_p)
                max_new_tokens=64,  # mex number of tokens to generate in the output
                repetition_penalty=1.1  # without this output begins repeating
            )
        return cls._instance

    @classmethod
    def get_model_pipeline(cls):
        return HuggingFacePipeline(pipeline=cls()._instance.generate_text)#type: ignore

# local_model = LocalModel()