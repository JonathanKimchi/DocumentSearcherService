from langchain.document_loaders import S3FileLoader

from request_objects.LoaderGeneratorRequest import S3LoaderRequest

class S3FileLoaderGenerator:
    def __init__(self, request: S3LoaderRequest):
        self.bucket_name = request.bucket_name
        self.filenames = request.filenames

    def load(self):
        for filename in self.filenames:
            loader = S3FileLoader(self.bucket_name, filename)
            yield loader.load(), filename
