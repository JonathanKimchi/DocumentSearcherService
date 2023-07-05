from model.LocalModel import LocalModel
from model.OpenAssistantModel import OpenAssistantModel

class ModelFactory:
    _instances = {
        'local': OpenAssistantModel(),
        # add other model types here
    }

    @staticmethod
    def get_model(model_type):
        return ModelFactory._instances[model_type]

model_factory = ModelFactory()