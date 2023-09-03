from loader.DirectoryLoaderGenerator import DirectoryLoaderGenerator
from loader.S3FileLoaderGenerator import S3FileLoaderGenerator

import json

from request_objects.LoaderGeneratorRequest import DirectoryLoaderRequest, S3LoaderRequest

class LoaderGeneratorFactory:

    @staticmethod
    def create_loader(data_payload: dict):
        data_type = data_payload.get("type")
        data_details = data_payload.get("dataPayload", {})
        
        if data_type == "directory":
            directory = data_details.get("directory")
            request = DirectoryLoaderRequest(directory)
            return DirectoryLoaderGenerator(request)
        
        elif data_type == "s3":
            bucket_name = data_details.get("bucket_name")
            filename = data_details.get("filename")
            request = S3LoaderRequest(bucket_name, filename)
            return S3FileLoaderGenerator(request)
        
        else:
            raise ValueError(f"Unsupported loader type: {data_type}")

