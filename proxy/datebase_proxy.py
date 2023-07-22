import os
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from model.ModelFactory import model_factory
import time

class DatabaseProxy:
    def __init__(self):
        # TODO: deprecate VectorstoreIndexCreator. Make sure all new data is added to the db
        self.loader = DirectoryLoader('data')
        self.index = VectorstoreIndexCreator().from_documents(self.loader.load())
        self.embedding_function = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        self.db = Chroma(persist_directory='db', embedding_function=self.embedding_function)
        self.retriever = self.db.as_retriever()
        self.model_factory = model_factory

    def get_data(self, query: str, model_type: str = 'open-ai'):
        model = self.model_factory.get_model(model_type)
        llm = model.get_model_pipeline()
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=self.retriever, return_source_documents=True)

        start = time.time()
        res = qa(query)
        answer, source_docs = res['result'], res['source_documents']
        end = time.time()

        # Print the result
        print("\n\n> Question:")
        print(query)
        print(f"\n> Answer (took {round(end - start, 2)} s.):")
        print(answer)

        print('source docs found', source_docs)
        # Print the relevant sources used for the answer
        for document in source_docs:
            print("\n> " + document.metadata["source"] + ":")

        source_metadata = [document.metadata["source"] for document in source_docs]

        return self.combine_answer_with_sources(answer, source_metadata)

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
            
    def combine_answer_with_sources(self, answer: str, sources: list) -> str:
        return answer + '\n\n' + '\n\n'.join(sources)
        

database_proxy = DatabaseProxy()