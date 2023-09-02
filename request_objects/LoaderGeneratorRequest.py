from typing import List

class LoaderGeneratorRequest:
    pass

class DirectoryLoaderRequest(LoaderGeneratorRequest):
    def __init__(self, directory: str):
        self.directory = directory

class S3LoaderRequest(LoaderGeneratorRequest):
    def __init__(self, bucket_name: str, filenames: List[str]):
        self.bucket_name = bucket_name
        self.filenames = filenames
