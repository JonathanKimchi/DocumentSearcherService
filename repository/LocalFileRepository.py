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

class LocalFileRepository:
    def __init__(self):
        self.directory = 'data'
        # TODO: Add load_database() to constructor after adding error handling for when there is no data in the directory.

    def update_data(self, data: str, filename: str):
        original_extension = os.path.splitext(filename)[1]
        if original_extension != '.txt':
            original_extension = original_extension[1:]  # remove the dot from the extension
            filename = f"{os.path.splitext(filename)[0]}-{original_extension}.txt"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        with open(os.path.join(self.directory, filename), 'w') as f:
            f.write(data)

    def download_data(self, filename: str):
        file_path = os.path.join(self.directory, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = f.read()
            return data
        else:
            print(f"File {filename} not found.")
            return False

    def delete_data(self, filename: str) -> bool:
        """
        Delete data by file name.

        Args:
            filename (str): The name of the file to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        file_path = os.path.join(self.directory, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"Error while deleting {filename}: {e}")
                return False
        else:
            print(f"File {filename} not found.")
            return False
            
    def combine_answer_with_sources(self, answer: str, sources: list) -> str:
        return {
            "answer": answer,
            "sources": sources
        }
    
    def list_data(self) -> list:
        """
        List all the file names stored within the given directory along with mock data for other fields.

        Returns:
            list: A list of dictionaries containing data for each document.
        """
        files = os.listdir(self.directory)
        data = []
        
        for idx, file_name in enumerate(files, 1):
            doc_data = {
                "id": idx,  # Assuming a simple incremental ID based on the list index for now
                "name": file_name,
                "filepath": f"{self.directory}/{file_name}",
                "type": self.mock_file_type(file_name),  # Mock file type
                "date": self.mock_file_date(),  # Mock file date
                "status": self.mock_status()  # Mock status
            }
            data.append(doc_data)
        return data

    def mock_file_type(self, file_name: str) -> str:
        """Return a mock file type based on file extension."""
        _, ext = os.path.splitext(file_name)
        ext = ext.lower()

        file_types = {
            ".txt": "Text",
            ".pdf": "PDF",
            ".doc": "Word",
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
        

local_file_repository = LocalFileRepository()