import os
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from model.ModelFactory import model_factory
import time
import datetime
import random

from langchain.chat_models import ChatOpenAI

from langchain.llms import OpenAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from repository.S3FileRepository import S3FileRepository
from langchain.document_loaders import S3DirectoryLoader

class DatabaseProxy:
    def __init__(self, client_id):
        self.client_id = client_id
        self.s3_repository = S3FileRepository(client_id)
        # TODO: Add load_database() to constructor after adding error handling for when there is no data in the directory.
        # TODO: initialize different file repositories based on the client_id or based on the environment variable

    def set_client_id(self, client_id: str):
        self.client_id = client_id
        self.s3_repository.set_bucket_name(client_id)

    def get_client_id(self):
        return self.client_id
    
    def load_database(self):
        # TODO: deprecate VectorstoreIndexCreator. Make sure all new data is added to the db
        # TODO: replace this loader with a loaderFactory.
        self.loader = S3DirectoryLoader(bucket='speakeasy-s3-bucket', prefix=self.client_id)
        data = self.loader.load()
        texts = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0).split_documents(data)
        self.index = VectorstoreIndexCreator().from_documents(texts)
        self.embedding_function = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        self.db = Chroma(persist_directory='db', embedding_function=self.embedding_function)
        self.retriever = self.index.vectorstore.as_retriever(search_kwargs={"k": 10})
        # self.retriever = self.db.as_retriever()
        self.model_factory = model_factory

    def get_data(self, query: str, model_type: str = 'open-ai'):
        model = self.model_factory.get_model(model_type)
        llm = model.get_model_pipeline()
        compressor = LLMChainExtractor.from_llm(ChatOpenAI())
        compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=self.retriever)
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=compression_retriever, return_source_documents=True)

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

        return self.combine_answer_with_sources(answer, self.get_source_filenames(source_docs))
    
    def get_source_filenames(self, source_docs: list) -> list:
        source_full_filepaths = [document.metadata["source"] for document in source_docs]
        source_filenames = [os.path.basename(source_full_filepath) for source_full_filepath in source_full_filepaths]
        #now, dedupe the list
        source_filenames = list(dict.fromkeys(source_filenames))
        return source_filenames

    def update_data(self, data: bytes, filename: str):
        self.s3_repository.update_data(data, filename)
        self.load_database()  # Re-load the database

    def download_data(self, filename: str):
        return self.s3_repository.download_data(filename)

    def delete_data(self, filename: str) -> bool:
        result = self.s3_repository.delete_data(filename)
        if result:
            self.load_database()  # Re-load the database
        return result

    def list_data(self) -> list:
        return self.s3_repository.list_data()
            
    def combine_answer_with_sources(self, answer: str, sources: list) -> str:
        return {
            "answer": answer,
            "sources": sources
        }

    def mock_file_type(self, file_name: str) -> str:
        """Return a mock file type based on file extension."""
        _, ext = os.path.splitext(file_name)
        ext = ext.lower()

        file_types = {
            ".txt": "Text",
            ".pdf": "PDF",
            ".doc": "Word",
            ".docx": "Word",
            ".xls": "Excel"
        }
        return file_types.get(ext, "Unknown")

    def mock_file_date(self) -> str:
        """Return a mock file date."""
        today = datetime.date.today()
        offset = datetime.timedelta(days=random.randint(0, 100))
        return str(today - offset)

    def mock_status(self) -> str:
        """Return a mock status."""
        return "Active"
        

database_proxy = DatabaseProxy('data')