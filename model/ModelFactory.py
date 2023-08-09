from model.LocalModel import LocalModel
from model.LlamaModel import LlamaModel
from model.OpenAiModel import OpenAiModel
from model.BaseModel import BaseModel

class ModelFactory:
    _instances = {
        # 'local': LocalModel(),
        'open-ai': OpenAiModel(),#type: ignore
        # 'llama': LlamaModel()
        # add other model types heren
    }

    @staticmethod
    def get_model(model_type) -> BaseModel:
        return ModelFactory._instances[model_type]

model_factory = ModelFactory()