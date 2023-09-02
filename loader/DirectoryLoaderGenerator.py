import os
from request_objects.LoaderGeneratorRequest import DirectoryLoaderRequest

class DirectoryLoaderGenerator:
    def __init__(self, request: DirectoryLoaderRequest):
        self.directory = request.directory

    def load(self):
        for filename in os.listdir(self.directory):
            filepath = os.path.join(self.directory, filename)
            with open(filepath, 'r') as file:
                yield file.read(), filename
