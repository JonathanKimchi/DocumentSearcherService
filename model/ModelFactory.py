from model.LocalModel import LocalModel
from model.OpenAssistantModel import OpenAssistantModel
from model.OpenAiModel import OpenAiModel

class ModelFactory:
    _instances = {
        # 'local': LocalModel(),
        'open-ai': OpenAiModel(),#type: ignore
        # add other model types here
    }

    @staticmethod
    def get_model(model_type):
        return ModelFactory._instances[model_type]

model_factory = ModelFactory()