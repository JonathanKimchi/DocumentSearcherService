import os
import boto3
import datetime
import random

class S3FileRepository:
    def __init__(self, folder_name):
        self.s3_client = boto3.client('s3')
        self.bucket_name = 'speakeasy-s3-bucket'
        self.folder_name = folder_name
        # TODO: Add load_database() to constructor after adding error handling for when there is no data in the directory.

    def set_bucket_name(self, folder_name: str):
        self.folder_name = folder_name

    def update_data(self, data: bytes, filename: str):
        key = f"{self.folder_name}/{filename}"
        _, file_extension = os.path.splitext(filename)
        content_type_map = {
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }
        content_type = content_type_map.get(file_extension, 'application/octet-stream')
        self.s3_client.put_object(Body=data, Bucket=self.bucket_name, Key=key, ContentType=content_type)

    def download_data(self, filename: str):
        key = f"{self.folder_name}/{filename}"
        try:
            obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return obj['Body'].read()
        except Exception as e:
            print(f"File {filename} not found: {e}")
            return False

    def delete_data(self, filename: str) -> bool:
        key = f"{self.folder_name}/{filename}"
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            print(f"Error while deleting {filename}: {e}")
            return False

    def list_data(self) -> list:
        objects = self.s3_client.list_objects(Bucket=self.bucket_name, Prefix=f"{self.folder_name}/")
        data = []
        for idx, obj in enumerate(objects.get('Contents', []), 1):
            file_name = obj['Key'].replace(f"{self.folder_name}/", "")
            doc_data = {
                "id": idx,
                "name": file_name,
                "filepath": f"s3://{self.bucket_name}/{obj['Key']}",
                "type": self.mock_file_type(file_name),
                "date": self.mock_file_date(),
                "status": self.mock_status()
            }
            data.append(doc_data)
        return data

    def mock_file_type(self, file_name: str) -> str:
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
        today = datetime.date.today()
        offset = datetime.timedelta(days=random.randint(0, 100))
        return str(today - offset)

    def mock_status(self) -> str:
        return "Active"
