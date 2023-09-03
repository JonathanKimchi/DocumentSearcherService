import os
import boto3
import datetime
import random

class S3FileRepository:
    def __init__(self, bucket_name):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name
        # TODO: Add load_database() to constructor after adding error handling for when there is no data in the directory.

    def set_bucket_name(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.ensure_bucket_exists()

    def ensure_bucket_exists(self):
        """Ensure that the bucket exists. If not, create it."""
        try:
            buckets = [bucket['Name'] for bucket in self.s3_client.list_buckets()['Buckets']]
            if self.bucket_name not in buckets:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                print(f"Bucket {self.bucket_name} created.")
            else:
                print(f"Bucket {self.bucket_name} already exists.")
        except Exception as e:
            print(f"An error occurred while creating or checking the bucket: {e}")

    def update_data(self, data: bytes, filename: str):
        _, file_extension = os.path.splitext(filename)
        content_type_map = {
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            # ... Add other file types here as needed
        }
        content_type = content_type_map.get(file_extension, 'application/octet-stream')  # Default to binary data
        self.s3_client.put_object(Body=data, Bucket=self.bucket_name, Key=filename, ContentType=content_type)


    def download_data(self, filename: str):
        try:
            obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=filename)
            return obj['Body'].read()  # Now, it returns bytes
        except Exception as e:
            print(f"File {filename} not found: {e}")
            return False

    def delete_data(self, filename: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=filename)
            return True
        except Exception as e:
            print(f"Error while deleting {filename}: {e}")
            return False

    def list_data(self) -> list:
        objects = self.s3_client.list_objects(Bucket=self.bucket_name)
        data = []

        for idx, obj in enumerate(objects.get('Contents', []), 1):
            file_name = obj['Key']
            doc_data = {
                "id": idx,
                "name": file_name,
                "filepath": f"s3://{self.bucket_name}/{file_name}",
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
