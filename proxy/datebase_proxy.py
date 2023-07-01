
import os
from random import random
import string
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator

def get_data(query: str):
    # make calls to langchain document loaders
    loader = DirectoryLoader('data')
    documents = loader.load()
    index = VectorstoreIndexCreator().from_documents(documents)
    return index.query(query)

def update_data(data: str, filename: str):
    directory = 'data'
    original_extension = os.path.splitext(filename)[1]
    if original_extension != '.txt':
        original_extension = original_extension[1:]  # remove the dot from the extension
        filename = f"{os.path.splitext(filename)[0]}-{original_extension}.txt"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(os.path.join(directory, filename), 'w') as f:
        f.write(data)