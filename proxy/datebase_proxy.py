import os
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import NotionDirectoryLoader
from model.ModelFactory import model_factory
import time
import datetime
import random

from langchain.chat_models import ChatOpenAI

from langchain.llms import OpenAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from proxy.SlackProxy import SlackProxy
from proxy.SpeakeasyBackendProxy import SpeakeasyBackendProxy
from repository.S3FileRepository import S3FileRepository
from langchain.document_loaders import S3DirectoryLoader
from langchain.document_loaders import JSONLoader

from loader.notion import CONTENT_TYPE_JSON, NOTION_VERSION, load_notion, get_notion_loaders, convert_documents_into_text, get_notion_header

class DatabaseProxy:
    def __init__(self, client_id):
        self.client_id = client_id
        self.s3_repository = S3FileRepository(client_id)
        self.s3_repository_notion = S3FileRepository(self.get_notion_client_id())
        # TODO: Add load_database() to constructor after adding error handling for when there is no data in the directory.
        # TODO: initialize different file repositories based on the client_id or based on the environment variable

    def get_notion_client_id(self):
        return self.client_id + "_notion"

    def set_client_id(self, client_id: str):
        self.client_id = client_id
        self.s3_repository.set_folder_name(client_id)
        self.s3_repository_notion.set_folder_name(self.get_notion_client_id())

    def get_client_id(self):
        return self.client_id
    
    def save_slack_conversations_to_s3(self, slack_access_token):
        # Fetch list of all channels
        slack_proxy = SlackProxy(slack_access_token)
        channels = slack_proxy.fetch_channels()
        if not channels:
            # throw exception
            return
        
        for channel in channels:
            # Fetch messages from each channel
            messages = slack_proxy.fetch_messages_from_channel(channel['id'])
            if messages:
                # Convert messages to text string
                text_string = slack_proxy.convert_messages_into_text(messages)

                # Convert text string to bytes
                text_bytes = text_string.encode('utf-8')
                print(f"Uploading {channel['name']} to S3...")

                # Upload to S3
                self.s3_repository.update_data(data=text_bytes, filename=f"{channel['name']}.txt")
        return
    
    def save_notion_data_to_s3(self, notion_access_token):
        header = get_notion_header(notion_access_token)

        # Fetch list of all pages
        document_loaders = get_notion_loaders(header)
        if not document_loaders:
            return
        
        documents = []

        for document_loader in document_loaders:
            # Fetch messages from each channel
            documents.extend(document_loader.load())

        # Convert messages to text string
        text_string = convert_documents_into_text(documents)

        print("Notion: ", text_string)
        print(f"Uploading notion data to S3...")
        self.s3_repository.update_data(data=text_bytes, filename=f"notion_data.json")
    
    def load_database(self):
        # TODO: deprecate VectorstoreIndexCreator. Make sure all new data is added to the db
        # TODO: replace this loader with a loaderFactory.
        # TODO: don't make API calls here to save on cost.
        self.loader = S3DirectoryLoader(bucket='speakeasy-s3-bucket', prefix=self.client_id+"/")
        data = self.loader.load()

        # load the notion data
        found_files = self.s3_repository_notion.get_names_of_files()

        for file in found_files:
            # get_data
            file_data = self.s3_repository_notion.download_data(file)
            # write to disk in notion_db folder
            with open(f"notion_db/{file}", "wb") as f:
                f.write(file_data)
            # unzip the file, delete the zip file, and move the contents of the folder to the notion_db folder
            os.system(f"unzip notion_db/{file} -d notion_db")
            # delete the zip file
            #os.remove(f"notion_db/{file}")
            # load the notion data
            notion_loader = NotionDirectoryLoader("notion_db")
            notion_data = notion_loader.load()
            data.extend(notion_data)
            # delete the file locally
            os.remove(f"notion_db/{file}")
        
        texts = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0).split_documents(data)
        self.index = VectorstoreIndexCreator().from_documents(texts)
        self.embedding_function = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        self.db = Chroma(persist_directory='db', embedding_function=self.embedding_function)
        self.retriever = self.index.vectorstore.as_retriever(search_kwargs={"k": 10})

    def get_data(self, query: str, model_type: str = 'open-ai'):
        model = model_factory.get_model(model_type)
        llm = model.get_model_pipeline()
        # TODO: Add this back after we finish demos for latency testing.
        compressor = LLMChainExtractor.from_llm(ChatOpenAI(temperature=0.25))
        compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=self.retriever)
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

        return self.combine_answer_with_sources(answer, self.get_source_filenames(source_docs))
    
    def get_source_filenames(self, source_docs: list) -> list:
        source_full_filepaths = [document.metadata["source"] for document in source_docs]
        source_filenames = [os.path.basename(source_full_filepath) for source_full_filepath in source_full_filepaths]
        #now, dedupe the list
        source_filenames = list(dict.fromkeys(source_filenames))
        return source_filenames

    def update_data(self, data: bytes, filename: str):
        # if the data is a zip file, then upload it to the notion folder
        if filename.endswith(".zip"):
            self.s3_repository_notion.update_data(data, filename)
        else:
            self.s3_repository.update_data(data, filename)
        self.load_database()  # Reload the database

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