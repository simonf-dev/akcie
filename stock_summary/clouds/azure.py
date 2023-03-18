import logging
import pathlib
from enum import Enum

from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError,
ClientAuthenticationError
)

from azure.storage.fileshare import (
    ShareServiceClient,
    ShareClient,
    ShareFileClient
)

class MergeTactic(Enum):
    LOCAL = "local"
    MERGE = "merge"
    CLOUD = "cloud"

class Azure:
    FILE_SHARE = "stocksummary"

    def __init__(self, connection_str: str):
        self.connection_str = connection_str
        self._service_client: ShareServiceClient = ShareServiceClient.from_connection_string(connection_str)
        self.check_connection()
        self._share_client = self.get_share()
        try:
            self._share_client.create_share()
            logging.info("Creating share: %s", self.FILE_SHARE)

        except ResourceExistsError as ex:
            logging.info("ResourceExistsError:", ex.message)


    def check_connection(self) -> None:
        """ Checks connection and raises error if there is some problem."""
        try:
            self._service_client.get_service_properties()
        except Exception as e:
            logging.error("Unable to connect to the Azure client with connection string.")
            raise e

    def get_share(self) -> ShareClient:
        share_client = self._service_client.get_share_client(self.FILE_SHARE)
        return share_client




    def sync_file_up(self, local_path: pathlib.Path, dest_path: str) -> None:
        try:
            source_file = open(local_path, "rb")
            data = source_file.read()

            # Create a ShareFileClient from a connection string
            file_client: ShareFileClient = ShareFileClient.from_connection_string(
                self.connection_str, self.FILE_SHARE, dest_path)

            print("Uploading to:", self.FILE_SHARE + "/" + dest_path)
            file_client.upload_file(data)

        except ResourceExistsError as ex:
            print("ResourceExistsError:", ex.message)

        except ResourceNotFoundError as ex:
            print("ResourceNotFoundError:", ex.message)

    def sync_file_down(self, source_file_name: str, dst_file_name: pathlib.Path) -> None:
        try:
            # Create a ShareFileClient from a connection string
            file_client: ShareFileClient = ShareFileClient.from_connection_string(
                self.connection_str, self.FILE_SHARE, source_file_name)

            print("Downloading to:", dst_file_name)

            # Open a file for writing bytes on the local system
            with open(dst_file_name, "wb") as data:
                # Download the file from Azure into a stream
                stream = file_client.download_file()
                # Write the stream to the local file
                data.write(stream.readall())

        except ResourceNotFoundError as ex:
            print("ResourceNotFoundError:", ex.message)



