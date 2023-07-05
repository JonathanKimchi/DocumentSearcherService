from model.LocalModel import LocalModel

class ModelFactory:
    _instances = {
        'local': LocalModel(),
        # add other model types here
    }

    @staticmethod
    def get_model(model_type):
        return ModelFactory._instances[model_type]

model_factory = ModelFactory()