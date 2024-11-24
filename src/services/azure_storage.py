from azure.storage.blob import BlobServiceClient, ContentSettings
from src.core.config import get_settings
import uuid

settings = get_settings()

class AzureStorageService:
    def __init__(self):
        self.conn_string = settings.STORAGE_CONN_STRING
        self.container = settings.STORAGE_CONTAINER
        self.blob_service_client = BlobServiceClient.from_connection_string(self.conn_string)
        self.container_client = self.blob_service_client.get_container_client(self.container)

    async def upload_file(self, file_content: bytes, content_type: str) -> str:
        # Generate a unique filename using UUID
        file_extension = content_type.split('/')[-1]
        blob_name = f"{uuid.uuid4()}.{file_extension}"
        
        # Create proper content settings
        content_settings = ContentSettings(
            content_type=content_type
        )
        
        # Upload the file to Azure Blob Storage
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.upload_blob(
            file_content, 
            blob_type="BlockBlob",
            content_settings=content_settings
        )
        
        # Return the blob URL
        return blob_client.url 