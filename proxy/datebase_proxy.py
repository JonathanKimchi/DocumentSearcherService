import os
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from model.ModelFactory import model_factory

class DatabaseProxy:
    def __init__(self):
        self.loader = DirectoryLoader('data')
        self.index = VectorstoreIndexCreator().from_documents(self.loader.load())
        self.model_factory = model_factory

    def get_data(self, query: str, model_type: str = 'open-ai'):
        model = self.model_factory.get_model(model_type)
        llm = model.get_model_pipeline()
        return self.index.query(query, llm=llm)

    def update_data(self, data: str, filename: str):
        directory = 'data'
        original_extension = os.path.splitext(filename)[1]
        if original_extension != '.txt':
            original_extension = original_extension[1:]  # remove the dot from the extension
            filename = f"{os.path.splitext(filename)[0]}-{original_extension}.txt"
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, filename), 'w') as f:
            f.write(data)

database_proxy = DatabaseProxy()